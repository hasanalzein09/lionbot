import createMiddleware from "next-intl/middleware";
import { routing } from "@/lib/i18n/navigation";

export default createMiddleware(routing);

export const config = {
  // Match all pathnames except for
  // - API routes
  // - _next (Next.js internals)
  // - Static files (images, favicon, etc.)
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
