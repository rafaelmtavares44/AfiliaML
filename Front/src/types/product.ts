export interface Product {
  id: string;
  title: string;
  description: string;
  originalPrice: number;
  discountPrice: number;
  discountPercent: number;
  imageUrl: string;
  affiliateLink: string;
  category: string;
  seller: string;
  rating: number;
  soldCount: number;
  freeShipping: boolean;
  createdAt: Date;
  featured: boolean;
}

export interface DashboardStats {
  totalProducts: number;
  totalClicks: number;
  messagesShared: number;
  conversionRate: number;
}
