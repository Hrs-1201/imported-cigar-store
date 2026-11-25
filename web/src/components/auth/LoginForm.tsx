"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AuthScreen, Field, buttonClassName, inputClassName } from "@/components/auth/AuthScreen";
import { ApiRequestError, apiFetch } from "@/lib/api-client";
import { setSession } from "@/lib/auth";
import { safeNextPath } from "@/lib/paths";
import type { TokenResponse } from "@/types/api";

const loginSchema = z.object({
  email: z.string().trim().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  return (
    <Suspense fallback={<p className="px-6 py-16 text-muted">Loading…</p>}>
      <LoginFormFields />
    </Suspense>
  );
}

function LoginFormFields() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginValues) {
    setFormError(null);
    try {
      const session = await apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        auth: false,
        body: values,
      });
      setSession(session.access_token, session.user);
      const next = safeNextPath(searchParams.get("next"));
      if (next) {
        router.push(next);
      } else if (session.user.role === "admin") {
        router.push("/admin");
      } else {
        router.push("/");
      }
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        setFormError("Email or password is incorrect");
        return;
      }
      setFormError(error instanceof ApiRequestError ? error.message : "Something went wrong. Please try again.");
    }
  }

  return (
    <AuthScreen
      title="Login"
      alternate={
        <>
          New here?{" "}
          <Link href="/register" className="font-medium text-ink underline">
            Create an account
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError ? <p className="text-sm text-red-800">{formError}</p> : null}
        <Field id="email" label="Email" error={errors.email?.message}>
          <input
            id="email"
            type="email"
            autoComplete="email"
            className={inputClassName}
            aria-invalid={Boolean(errors.email)}
            {...register("email")}
          />
        </Field>
        <Field id="password" label="Password" error={errors.password?.message}>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            className={inputClassName}
            aria-invalid={Boolean(errors.password)}
            {...register("password")}
          />
        </Field>
        <button type="submit" className={buttonClassName} disabled={isSubmitting}>
          {isSubmitting ? "Signing in…" : "Login"}
        </button>
      </form>
    </AuthScreen>
  );
}
