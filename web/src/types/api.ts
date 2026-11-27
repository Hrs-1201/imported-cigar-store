export type UserRole = "customer" | "admin";

export type UserPublic = {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  role: UserRole;
  age_verified: boolean;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: UserPublic;
};

export type RegisterRequest = {
  full_name: string;
  email: string;
  phone?: string | null;
  password: string;
  date_of_birth: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type Strength = "mild" | "mild_to_medium" | "medium" | "medium_to_full" | "full";

export type ProductShape =
  | "parejo"
  | "toro"
  | "robusto"
  | "churchill"
  | "figurado"
  | "lancero"
  | "corona"
  | "gordo"
  | "other";

export type ProductImage = {
  id: string;
  public_path: string;
  alt_text: string;
};

export type ProductRating = {
  source_name: string;
  score: string;
};

export type ProductCard = {
  id: string;
  slug: string;
  name: string;
  brand: string;
  category_slug: string;
  category_name: string;
  subtype: string | null;
  short_description: string | null;
  price_inr: string;
  box_price_inr: string | null;
  units_per_box: number | null;
  units_per_pack: number | null;
  stock_qty: number;
  low_stock: boolean;
  in_stock: boolean;
  origin_country: string | null;
  origin_label: string | null;
  smoking_time_min_minutes: number | null;
  smoking_time_max_minutes: number | null;
  intensity: number | null;
  strength: Strength | null;
  shape: ProductShape | null;
  size_label: string | null;
  is_founder_pick: boolean;
  founder_rank: number | null;
  is_new_arrival: boolean;
  primary_image: ProductImage | null;
  ratings: ProductRating[];
  extra_ratings_count: number;
};

export type ProductDetail = ProductCard & {
  description: string | null;
  sku: string;
  images: ProductImage[];
};

export type ProductPage = {
  items: ProductCard[];
  total: number;
  page: number;
  page_size: number;
};

export type ProductCardList = {
  items: ProductCard[];
};

export type BrandList = {
  items: string[];
};

export type Category = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  sort_order: number;
};

export type ContactRequest = {
  name: string;
  email: string;
  phone?: string | null;
  subject: string;
  message: string;
};

export type ContactCreated = {
  id: string;
  status: "new" | "read" | "archived";
};
