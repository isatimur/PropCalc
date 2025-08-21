"use client";

import * as Sentry from "@sentry/nextjs";

export default function SentryExamplePage() {
  return (
    <div>
      <h1>Sentry Example Page</h1>
      <p>This page is used to test Sentry integration.</p>
      <button
        onClick={() => {
          throw new Error("Sentry Frontend Error");
        }}
      >
        Throw error
      </button>
    </div>
  );
}
