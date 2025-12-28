import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      // Allow flexibility while the codebase stabilizes.
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": "warn",
      "react-hooks/exhaustive-deps": "error",
      "react-hooks/rules-of-hooks": "warn",
      "react-hooks/set-state-in-effect": "error",
      "@next/next/no-img-element": "warn",
    },
  },
]);

export default eslintConfig;
