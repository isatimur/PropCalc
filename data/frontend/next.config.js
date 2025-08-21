/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig;

// Injected content via Sentry wizard below

// const { withSentryConfig } = require("@sentry/nextjs");

// module.exports = withSentryConfig(
//   nextConfig,
//   {
//     // For all available options, see:
//     // https://www.npmjs.com/package/@sentry/webpack-plugin#options

//     org: "iti-d7",
//     project: "javascript-nextjs",

//     // Only print logs for uploading source maps in CI
//     silent: !process.env.CI,

//     // For all available options, see:
//     // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

//     // Upload a larger set of source maps for prettier stack traces (increases build time)
//     widenClientFileUpload: true,

//     // Route browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers (increases server load in the event of a Sentry outage):
//     // Note: Check that the original route is not public before proceeding to avoid the Intent to Reapply for a public route error.
//     tunnelRoute: "/monitoring",

//     // Hide source maps from browser client
//     hideSourceMaps: true,

//     // Disable automatic instrumentation of Vercel Cron Monitors (We'll do it manually)
//     disableLogger: true,
//   },
//   {
//     // For all available options, see:
//     // https://docs.sentry.io/platforms/javascript/guides/nextjs/

//     // Upload a larger set of source maps for prettier stack traces (increases build time)
//     widenClientFileUpload: true,

//     // Set an upload delay to ensure all source maps are uploaded before the build completes
//     uploadDelay: 1000,

//     // Disable automatic instrumentation of Vercel Cron Monitors (We'll do it manually)
//     disableLogger: true,
//   }
// );
