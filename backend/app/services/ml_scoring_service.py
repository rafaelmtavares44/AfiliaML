# ============================================
# AfiliaML — Service de ML Scoring (scikit-learn)
# Classificação de relevância de produtos
# Usa GaussianNB do scikit-learn (antes era manual em TS)
# ============================================

import json
import math
import numpy as np
from datetime import datetime, timezone
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle
import base64

from app.utils.redis_client import get_redis
from app.repositories.product_repo import product_repository
from app.repositories.click_event_repo import click_event_repository
from app.repositories.share_event_repo import share_event_repository
from app.repositories.price_history_repo import price_history_repository
from app.services.ml_audit_service import ml_audit_service

FEATURE_NAMES = [
    "discountPct", "priceNormalized", "ratingAverage", "ratingCountNorm",
    "soldQuantityNorm", "freeShipping", "clicksLast7Days", "sharesLast7Days",
    "conversionRate", "pageRankScore", "priceTrend", "categoryEncoded",
]


def _hash_category(category: str) -> float:
    """Hash numérico simples para categoria."""
    if not category:
        return 0.0
    h = 0
    for c in category:
        h = ((h << 5) - h + ord(c)) & 0xFFFFFFFF
    return (abs(h) % 1000) / 1000


class MLScoringService:
    """Serviço de ML scoring usando scikit-learn."""

    async def extract_features(self, product_id: str) -> dict:
        """Extrair features numéricas de um produto."""
        r = get_redis()
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        price = float(produto.get("price") or 0)
        old_price = float(produto.get("oldPrice") or 0)

        # Desconto
        discount_pct = ((old_price - price) / old_price * 100) if old_price > price else 0

        # Preço normalizado
        max_price = float(await r.get("ml:max_price") or 10000)
        price_normalized = price / max_price if max_price > 0 else 0

        # Rating e sold
        rating_average = float(produto.get("ratingAverage") or 0)
        rating_count = int(produto.get("ratingCount") or 0)
        sold_quantity = int(produto.get("soldQuantity") or 0)

        rating_count_norm = min(rating_count / 1000, 1)
        sold_quantity_norm = min(sold_quantity / 5000, 1)
        free_shipping = 1.0 if produto.get("freeShipping") else 0.0

        # Cliques últimos 7 dias
        import time
        sete_dias_atras = time.time() * 1000 - 7 * 24 * 60 * 60 * 1000
        clicks_all = await click_event_repository.analytics_por_produto(product_id)
        clicks_last_7 = len([
            c for c in (clicks_all or [])
            if datetime.fromisoformat(str(c.get("createdAt", ""))).timestamp() * 1000 > sete_dias_atras
        ]) if clicks_all else 0

        # Shares últimos 7 dias
        shares_all = await share_event_repository.listar_por_produto(product_id)
        shares_last_7 = len([
            s for s in (shares_all or [])
            if datetime.fromisoformat(str(s.get("createdAt", ""))).timestamp() * 1000 > sete_dias_atras
        ]) if shares_all else 0

        # Taxa de conversão
        total_clicks = await click_event_repository.contar_por_produto(product_id)
        total_shares = await share_event_repository.contar_por_produto(product_id)
        conversion_rate = min(total_clicks / total_shares, 5) / 5 if total_shares > 0 else 0

        # PageRank
        pr_score = await r.hget("graph:pagerank", product_id)
        page_rank_score = float(pr_score) if pr_score else 0

        # Tendência de preço
        try:
            tendencia = await price_history_repository.calcular_tendencia(product_id)
            price_trend = 1 if tendencia == "subindo" else (-1 if tendencia == "caindo" else 0)
        except Exception:
            price_trend = 0

        # Categoria codificada
        category_encoded = _hash_category(str(produto.get("category", "")))

        return {
            "discountPct": discount_pct / 100,
            "priceNormalized": price_normalized,
            "ratingAverage": rating_average / 5,
            "ratingCountNorm": rating_count_norm,
            "soldQuantityNorm": sold_quantity_norm,
            "freeShipping": free_shipping,
            "clicksLast7Days": min(clicks_last_7 / 100, 1),
            "sharesLast7Days": min(shares_last_7 / 50, 1),
            "conversionRate": conversion_rate,
            "pageRankScore": min(page_rank_score * 10, 1),
            "priceTrend": (price_trend + 1) / 2,
            "categoryEncoded": category_encoded,
        }

    async def train_model(self) -> dict:
        """Treinar modelo Naive Bayes com scikit-learn."""
        r = get_redis()
        print("🤖 Treinando modelo Naive Bayes (scikit-learn)...")

        produtos = await product_repository.listar_todos()
        if len(produtos) < 5:
            raise ValueError("Insuficiente: mínimo de 5 produtos para treinar")

        # Salvar preço máximo
        max_price = max(float(p.get("price") or 0) for p in produtos)
        await r.set("ml:max_price", str(max_price))

        # Extrair features
        features = []
        product_ids = []
        for produto in produtos:
            if not produto:
                continue
            try:
                pid = str(produto.get("id", ""))
                fv = await self.extract_features(pid)
                features.append([fv[name] for name in FEATURE_NAMES])
                product_ids.append(pid)
            except Exception:
                pass

        if len(features) < 5:
            raise ValueError("Insuficiente: features extraídas de menos de 5 produtos")

        X = np.array(features)

        # Normalizar
        scaler = MinMaxScaler()
        X_normalized = scaler.fit_transform(X)

        # Labels: cliques acima da mediana -> positiva
        click_counts = []
        for pid in product_ids:
            count = await click_event_repository.contar_por_produto(pid)
            click_counts.append(count)

        sorted_clicks = sorted(click_counts)
        mediana = sorted_clicks[len(sorted_clicks) // 2]
        y = np.array([1 if c > mediana else 0 for c in click_counts])

        # Split 80/20
        X_train, X_test, y_train, y_test = train_test_split(
            X_normalized, y, test_size=0.2, random_state=42
        )

        # Treinar modelo
        model = GaussianNB()
        model.fit(X_train, y_train)

        # Avaliar
        accuracy = model.score(X_test, y_test) if len(X_test) > 0 else 0.0

        # Feature importance (diferença de médias entre classes)
        pos_mask = y_train == 1
        neg_mask = y_train == 0
        pos_means = X_train[pos_mask].mean(axis=0) if pos_mask.any() else np.zeros(len(FEATURE_NAMES))
        neg_means = X_train[neg_mask].mean(axis=0) if neg_mask.any() else np.zeros(len(FEATURE_NAMES))
        importance = np.abs(pos_means - neg_means)

        features_importance = sorted(
            [{"feature": FEATURE_NAMES[i], "importance": round(float(importance[i]), 4)}
             for i in range(len(FEATURE_NAMES))],
            key=lambda x: x["importance"],
            reverse=True,
        )

        # Salvar modelo no Redis (serializado com pickle + base64)
        model_version = f"nb_sklearn_v1_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        model_data = {
            "model_pickle": base64.b64encode(pickle.dumps(model)).decode("ascii"),
            "scaler_pickle": base64.b64encode(pickle.dumps(scaler)).decode("ascii"),
            "accuracy": accuracy,
            "trainedAt": datetime.now(timezone.utc).isoformat(),
            "totalSamples": len(features),
            "modelVersion": model_version,
            "featureNames": FEATURE_NAMES,
        }
        await r.set("ml:model:naive_bayes", json.dumps(model_data))

        print(f"🤖 Modelo treinado! Accuracy: {accuracy * 100:.1f}%, Samples: {len(features)}")

        return {
            "accuracy": round(accuracy, 4),
            "featuresImportance": features_importance,
            "trainedAt": model_data["trainedAt"],
            "totalSamples": len(features),
        }

    async def predict(self, product_id: str) -> dict:
        """Predição para um produto."""
        r = get_redis()

        model_json = await r.get("ml:model:naive_bayes")
        if not model_json:
            raise ValueError("Modelo não treinado. Execute POST /api/ml/train primeiro.")

        model_data = json.loads(model_json)
        model: GaussianNB = pickle.loads(base64.b64decode(model_data["model_pickle"]))
        scaler: MinMaxScaler = pickle.loads(base64.b64decode(model_data["scaler_pickle"]))

        # Extrair e normalizar features
        fv = await self.extract_features(product_id)
        raw_features = [fv[name] for name in FEATURE_NAMES]
        X = scaler.transform([raw_features])

        # Predição
        proba = model.predict_proba(X)[0]
        # proba[0] = P(negativa), proba[1] = P(positiva)
        score = float(proba[1]) if len(proba) > 1 else float(proba[0])

        # Classificar
        if score >= 0.65:
            classification = "alta_relevancia"
        elif score >= 0.35:
            classification = "media_relevancia"
        else:
            classification = "baixa_relevancia"

        # Top features (log-probability contributions)
        feature_contributions = []
        for i, name in enumerate(FEATURE_NAMES):
            contrib = float(X[0][i]) * score  # Simplified contribution
            feature_contributions.append({
                "feature": name,
                "value": round(raw_features[i], 4),
                "contribution": round(contrib, 4),
            })
        feature_contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        top_features = feature_contributions[:3]

        result = {
            "productId": product_id,
            "score": round(score, 4),
            "classification": classification,
            "topFeatures": top_features,
            "predictedAt": datetime.now(timezone.utc).isoformat(),
        }

        # Registrar auditoria
        await ml_audit_service.registrar_predicao({
            "productId": product_id,
            "score": result["score"],
            "classification": classification,
            "featuresSnapshot": fv,
            "modelVersion": model_data.get("modelVersion", "unknown"),
        })

        return result

    async def predict_batch(self, product_ids: list[str]) -> list[dict]:
        resultados = []
        for pid in product_ids:
            try:
                result = await self.predict(pid)
                resultados.append(result)
            except Exception:
                pass
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados

    async def get_model_status(self) -> dict:
        r = get_redis()
        model_json = await r.get("ml:model:naive_bayes")
        if not model_json:
            return {"status": "not_trained", "message": "Nenhum modelo treinado ainda."}

        model_data = json.loads(model_json)
        return {
            "status": "trained",
            "modelVersion": model_data.get("modelVersion"),
            "accuracy": model_data.get("accuracy"),
            "totalSamples": model_data.get("totalSamples"),
            "trainedAt": model_data.get("trainedAt"),
            "featureCount": len(model_data.get("featureNames", [])),
            "featuresUsed": model_data.get("featureNames", []),
        }


ml_scoring_service = MLScoringService()
