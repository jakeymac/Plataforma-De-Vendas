import globals from "globals";
import pluginJs from "@eslint/js";


/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    files: ["**/*.js"], 
    languageOptions: {
      sourceType: "script",
      globals: globals.browser 
    },
    rules: {
      "no-unused-vars": "error",
      "no-console": "off",
      "indent": ["error", 4, {
        "SwitchCase": 1,
        "MemberExpression": 1,
        "CallExpression": { "arguments": "first" },
        "ignoredNodes": [
          "CallExpression > FunctionExpression.callee > BlockStatement.body",
          "CallExpression > ArrowFunctionExpression > BlockStatement.body",
          "ExpressionStatement > CallExpression",
          "CallExpression > MemberExpression"
        ]
      }],
      "newline-per-chained-call": ["off"],
      "implicit-arrow-linebreak": "off",
      "quotes": ["error", "single", {"avoidEscape": true, "allowTemplateLiterals": true }],
      "semi": ["error", "always"],
      "prefer-arrow-callback": ["error", 
        { "allowNamedFunctions": false ,
          "allowUnboundThis": true
        }],
    },
  },
];