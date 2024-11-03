TEMPLATES = {
    "assets/input.css": """@tailwind base;
@tailwind components;
@tailwind utilities;""",
    
    "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/*.py",    
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: ["cupcake", "dim"],
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}""",
    
    "main.py": """from fasthtml.common import *

app, rt = fast_app()

@rt("/")
def get():
    return Titled("FastHTML with Tailwind",
        Main(
            H1("Welcome to FastHTML", cls="text-4xl font-bold"),
            P("A simple template to get you started.", cls="mt-4 text-lg"),
        )
    )

serve()"""
}