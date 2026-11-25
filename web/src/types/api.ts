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
