
import markdown
import os

def generate_html_report():
    input_path = 'reports/User_Conversion_Analysis_Report.md'
    output_path = 'reports/User_Conversion_Analysis_Report.html'
    
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    # CSS for professional report look
    css = """
    <style>
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            background-color: #fff;
        }
        h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        h3 { color: #2980b9; margin-top: 25px; }
        h4 { color: #2c3e50; margin-top: 20px; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }
        pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #e9ecef; }
        blockquote { border-left: 4px solid #3498db; margin: 0; padding-left: 15px; color: #555; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; color: #2c3e50; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; margin: 20px 0; }
        .print-button {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        @media print {
            .print-button { display: none; }
            body { padding: 0; max-width: 100%; }
        }
    </style>
    """
    
    # Convert MD to HTML
    html_content = markdown.markdown(text, extensions=['tables', 'fenced_code'])
    
    # Add print button script
    script = """
    <script>
        function printReport() {
            window.print();
        }
    </script>
    """
    
    # Wrap in full HTML structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>User Conversion Analysis Report</title>
        {css}
    </head>
    <body>
        <button class="print-button" onclick="printReport()">Save as PDF / Print</button>
        {html_content}
        {script}
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    print(f"✅ Report generated: {output_path}")
    print("👉 Open this file in your browser and click 'Save as PDF / Print'")

if __name__ == "__main__":
    generate_html_report()
