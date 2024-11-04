# Base Tailwind templates
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
  plugins: [],
}""",
    
    "main.py": """from fasthtml.common import *

# Prevent FOUC (Flash of Unstyled Content)
fouc_script = Script('''
(function() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('dark', savedTheme === 'dark' || (!savedTheme && prefersDark));
})();
''')

# Link to compiled CSS
tailwind_css = Link(rel="stylesheet", href="/assets/output.css", type="text/css")

# Initialize app with proper headers
app, rt = fast_app(
    pico=False,
    surreal=False,
    live=True,
    hdrs=(fouc_script, tailwind_css),
)


def theme_toggle():
    theme_checkbox = Input(
        type='checkbox',
        id='theme-toggle'      
    )  

    return Label(
        theme_checkbox,       
        Span("Light", cls="hidden dark:inline-block"),
        Span("Dark", cls="inline-block dark:hidden"),
        theme_toggle_script,       
        cls='inline-flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg cursor-pointer'
    )

theme_toggle_script = Script('''
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    function updateTheme(isDark) {
        html.classList.toggle('dark', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeToggle.checked = isDark;
    }

    // Set initial theme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    updateTheme(savedTheme === 'dark' || (!savedTheme && prefersDark));

    // Listen for toggle changes
    themeToggle.addEventListener('change', function() {
        updateTheme(this.checked);
    });
});
''')

@rt("/")
def get():
    return Titled("FastHTML with Tailwind",
        Main(
            Div(cls="min-h-screen bg-white dark:bg-gray-900",
                Div(cls="container mx-auto px-4 py-8",
                    Div(cls="flex justify-between items-center",
                        H1("Welcome to FastHTML", 
                           cls="text-4xl font-bold text-gray-900 dark:text-white"),
                        theme_toggle()
                    ),
                    P("A simple template to get you started.", 
                      cls="mt-4 text-lg text-gray-600 dark:text-gray-300")
                )
            )
        )
    )

serve()"""
}

# Tailwind + DaisyUI templates
TEMPLATES_DAISY = {
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
    themes: ["retro", "night"],
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}""",
    
    "main.py": """from fasthtml.common import *


# Prevent FOUC (Flash of Unstyled Content)
fouc_script = Script('''
(function() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'night' : 'retro');
    document.documentElement.setAttribute('data-theme', theme);
})();
''')

# Link to compiled CSS
tailwind_css = Link(rel="stylesheet", href="/assets/output.css", type="text/css")

# Initialize app with proper headers and theme
app, rt = fast_app(
    pico=False,
    surreal=False,
    live=True,
    hdrs=(fouc_script, tailwind_css),
    htmlkw=dict(data_theme="retro")
)


def theme_toggle():
    theme_checkbox = Input(
        type='checkbox',
        value='night',
        cls='theme-controller',
        id='theme-toggle'      
    )  

    return Label(
        theme_checkbox,       
        Span("Light", cls="swap-off"),
        Span("Dark", cls="swap-on"),
        theme_toggle_script,       
        cls='btn btn-ghost swap'
    )

theme_toggle_script = Script('''
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    function updateTheme(isDark) {
        html.setAttribute('data-theme', isDark ? 'dim' : 'retro');
        localStorage.setItem('theme', isDark ? 'dim' : 'retro');
        themeToggle.checked = isDark;
    }

    // Set initial theme
    const savedTheme = localStorage.getItem('theme');
    updateTheme(savedTheme === 'dim');

    // Listen for toggle changes
    themeToggle.addEventListener('change', function() {
        updateTheme(this.checked);
    });
});
''')

@rt("/")
def get():
    return Titled("FastHTML with Tailwind + DaisyUI",
        Main(
            Div(cls="min-h-screen bg-base-100",
                Div(cls="container mx-auto px-4 py-8",
                    Div(cls="flex justify-between items-center",
                        H1("Welcome to FastHTML", 
                           cls="text-4xl font-bold text-primary"),
                        theme_toggle()
                    ),
                    P("A simple template to get you started.", 
                      cls="mt-4 text-lg text-base-content")
                )
            )
        )
    )

serve()"""
}