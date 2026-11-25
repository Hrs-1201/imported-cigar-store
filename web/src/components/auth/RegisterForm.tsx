"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AuthScreen, Field, buttonClassName, inputClassName } from "@/components/auth/AuthScreen";
import { ApiRequestError, apiFetch } from "@/lib/api-client";
import { setSession } from "@/lib/auth";
import type { RegisterRequest, TokenResponse } from "@/types/api";

const registerSchema = z
  .object({
    full_name: z.string().trim().min(1, "Name is required").max(200),
    email: z.string().trim().email("Enter a valid email"),
    phone: z.string().trim().max(20, "Phone must be 20 characters or fewer"),
    password: z.string().min(8, "Password must be at least 8 characters").max(128),
    confirm_password: z.string(),
    date_of_birth: z.string().min(1, "Date of birth is required"),
    confirm_age: z.boolean().refine((value) => value, {
      message: "Confirm that you are 21 or older and not buying for a minor",
    }),
  })
  .refine((values) => values.password === values.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type RegisterValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      phone: "",
      password: "",
      confirm_password: "",
      date_of_birth: "",
      confirm_age: false,
    },
  });

  async function onSubmit(values: RegisterValues) {
    setFormError(null);
    const body: RegisterRequest = {
      full_name: values.full_name,
      email: values.email,
      phone: values.phone ? values.phone : null,
      password: values.password,
      date_of_birth: values.date_of_birth,
    };
    try {
      const session = await apiFetch<TokenResponse>("/auth/register", {
        method: "POST",
        auth: false,
        body,
      });
      setSession(session.access_token, session.user);
      router.push("/account");
    } catch (error) {
      setFormError(error instanceof ApiRequestError ? error.message : "Something went wrong. Please try again.");
    }
  }

  return (
    <AuthScreen
      title="Create an account"
      alternate={
        <>
          Already registered?{" "}
          <Link href="/login" className="font-medium text-ink underline">
            Login
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError ? <p className="text-sm text-red-800">{formError}</p> : null}
        <Field id="full_name" label="Full name" error={errors.full_name?.message}>
          <input id="full_name" autoComplete="name" className={inputClassName} {...register("full_name")} />
        </Field>
        <Field id="email" label="Email" error={errors.email?.message}>
          <input id="email" type="email" autoComplete="email" className={inputClassName} {...register("email")} />
        </Field>
        <Field id="phone" label="Phone (optional)" error={errors.phone?.message}>
          <input id="phone" type="tel" autoComplete="tel" className={inputClassName} {...register("phone")} />
        </Field>
        <Field id="password" label="Password" error={errors.password?.message}>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            className={inputClassName}
            {...register("password")}
          />
        </Field>
        <Field id="confirm_password" label="Confirm password" error={errors.confirm_password?.message}>
          <input
            id="confirm_password"
            type="password"
            autoComplete="new-password"
            className={inputClassName}
            {...register("confirm_password")}
          />
        </Field>
        <Field id="date_of_birth" label="Date of birth" error={errors.date_of_birth?.message}>
          <input id="date_of_birth" type="date" autoComplete="bday" className={inputClassName} {...register("date_of_birth")} />
        </Field>
        <div>
          <label className="flex items-start gap-2 text-sm">
            <input type="checkbox" className="mt-1" {...register("confirm_age")} />
            <span>I confirm I am 21 or older and I am not buying for a minor</span>
          </label>
          {errors.confirm_age ? <p className="mt-1 text-sm text-red-800">{errors.confirm_age.message}</p> : null}
        </div>
        <button type="submit" className={buttonClassName} disabled={isSubmitting}>
          {isSubmitting ? "Creating account…" : "Create account"}
        </button>
      </form>
    </AuthScreen>
  );
}
