"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Field, buttonClassName, inputClassName } from "@/components/auth/AuthScreen";
import { ApiRequestError, apiFetch } from "@/lib/api-client";
import type { ContactCreated } from "@/types/api";

const contactSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(200),
  email: z.string().trim().email("Enter a valid email").max(320),
  phone: z.string().trim().max(20, "Phone is too long"),
  subject: z.string().trim().min(1, "Subject is required").max(200),
  message: z.string().trim().min(1, "Message is required").max(5000),
});

type ContactValues = z.infer<typeof contactSchema>;

export function ContactForm() {
  const [sent, setSent] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ContactValues>({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: "", email: "", phone: "", subject: "", message: "" },
  });

  async function onSubmit(values: ContactValues) {
    setFormError(null);
    try {
      await apiFetch<ContactCreated>("/contact", {
        method: "POST",
        auth: false,
        body: {
          name: values.name,
          email: values.email,
          phone: values.phone.trim() ? values.phone.trim() : null,
          subject: values.subject,
          message: values.message,
        },
      });
      setSent(true);
    } catch (error) {
      setFormError(error instanceof ApiRequestError ? error.message : "Something went wrong. Please try again.");
    }
  }

  if (sent) {
    return (
      <p role="status" className="mt-8 font-serif text-2xl">
        Thank you. Your message is with the shop.
      </p>
    );
  }

  return (
    <form className="mt-8 space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
      {formError ? <p className="text-sm text-red-800">{formError}</p> : null}
      <Field id="contact-name" label="Name" error={errors.name?.message}>
        <input id="contact-name" autoComplete="name" className={inputClassName} {...register("name")} />
      </Field>
      <Field id="contact-email" label="Email" error={errors.email?.message}>
        <input id="contact-email" type="email" autoComplete="email" className={inputClassName} {...register("email")} />
      </Field>
      <Field id="contact-phone" label="Phone (optional)" error={errors.phone?.message}>
        <input id="contact-phone" type="tel" autoComplete="tel" className={inputClassName} {...register("phone")} />
      </Field>
      <Field id="contact-subject" label="Subject" error={errors.subject?.message}>
        <input id="contact-subject" className={inputClassName} {...register("subject")} />
      </Field>
      <Field id="contact-message" label="Message" error={errors.message?.message}>
        <textarea id="contact-message" rows={5} className={inputClassName} {...register("message")} />
      </Field>
      <button type="submit" className={buttonClassName} disabled={isSubmitting}>
        {isSubmitting ? "Sending…" : "Send message"}
      </button>
    </form>
  );
}
