from flask import render_template_string

def email_html_template(title, message, type='success'):
    icon_map = {
        'success': ('<i class="fa-solid fa-check"></i>', 'bg-green-500'),
        'error': ('<i class="fa-solid fa-xmark"></i>', 'bg-red-500'),
        'info': ('<i class="fa-solid fa-info-circle"></i>', 'bg-blue-500'),
        'warning': ('<i class="fa-solid fa-exclamation-triangle"></i>', 'bg-yellow-400'),
    }

    icon_html, bg_class = icon_map.get(type, icon_map['info'])

    return render_template_string(f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" integrity="sha512-Evv84Mr4kqVGRNSgIGL/F/aIDqQb7xQ2vcrdIwxfjThSH8CSR7PBEakCr51Ck+w+/U6swU2Im1vVX0SVk9ABhg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 text-gray-800">
        <section class="min-h-screen flex items-center justify-center p-6">
            <div class="p-6 rounded-md shadow-md border-l-4 {bg_class} bg-white max-w-md w-full">
                <div class="flex items-center space-x-3">
                    <div class="text-2xl">{icon_html}</div>
                    <h2 class="text-xl font-semibold">{title}</h2>
                </div>
                <p class="mt-3 text-gray-700">{message}</p>
            </div>
        </section>
    </body>
    </html>
    """)
