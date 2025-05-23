template_str = """

 <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Structure Analysis Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .dashboard-header {
            grid-column: 1 / -1;
            display: -webkit-box;
            justify-content: space-between;
            -webkit-box-pack: justify;
            align-items: center;
            border-bottom: 2px solid #5271ff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .section-card {
            background: #fff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-top: 4px solid #5271ff;
            margin-bottom: 10px;
        }
        .section-header {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #eee;
            display: -webkit-box;
            justify-content: space-between;
            -webkit-box-pack: justify;
            align-items: center;
        }
        .section-body {
            font-size: 0.9rem;
        }
        .status-tag {
            font-size: 0.7rem;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 500;
        }
        .status-pass {
            background: #e7f6e7;
            color: #2e7d32;
        }
        .status-warning {
            background: #fff8e1;
            color: #ff8f00;
        }
        .status-error {
            background: #ffebee;
            color: #c62828;
        }
        .issue-list {
            list-style-type: none;
            padding-left: 0;
            margin: 10px 0;
        }
        .issue-item {
            background: #f5f5f5;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 8px;
            font-size: 0.85rem;
            border-left: 3px solid #ff7043;
        }
        .issue-item.sequence {
            border-left-color: #ffa726;
        }
        .issue-item.style {
            border-left-color: #7e57c2;
        }
        .summary-box {
            grid-column: 1 / -1;
            background: #f5f7ff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }
        .summary-stats {
            display: -webkit-box;
            justify-content: space-between;
            -webkit-box-pack: justify;
            flex-wrap: wrap;
        }
        .stat-item {
            flex: 1;
            min-width: 150px;
            text-align: center;
            padding: 12px;
            background: white;
            border-radius: 6px;
            box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
        }
        .stat-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #5271ff;
        }
        .references-issues {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
        .reference-item {
            background: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        h1 {
            margin: 0;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>JISEBI Manuscript Report</h1>
        <div>Report generated on {{ current_time }}</div>
    </div>

    <div class="summary-box">
        <h2>Document Overview</h2>
        <h3> Title: {{ title }} </h3>
        <div class="summary-stats">
            <div class="stat-item">
                <div class="stat-label">Sections with Issue</div>
                <div class="stat-value">{{ total_issues }}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Sections with Sequence Issues</div>
                <div class="stat-value">{{ sections_with_sequence_issues }}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Sections with Style Issues</div>
                <div class="stat-value"> {{ sections_with_style_issues }} </div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Missing Sections</div>
                <div class="stat-value"> {{ sections_with_not_found_issues }} </div>
            </div>
        </div>
    </div>

    <div class="dashboard">
    {% for section in sections %}
        {% if "literature_review" not in data %}
        {% else %}
        <div class="section-card">
            <div class="section-header">
                {{ section | title }}
                {% if data[section]["section_issue"]["not_found"] == [] and data[section]["section_issue"]["sequence"] == [] and (data[section]["body"] == {} or "body" not in data[section]) and (data[section]["heading"] == {} or "heading" not in data[section]) %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data[section]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 

                {% if (data[section]["body"] != {} and "body" in data[section]) or (data[section]["heading"] != {} and "heading" in data[section]) %}
                    <span class="status-tag status-error"> {{ data[section]["body"] | length + data[section]["heading"] | length}} Style Issues</span>
                {% endif %}

                {% if data[section]["section_issue"]["not_found"] != [] %}
                    <span class="status-tag status-error"> Missing </span>
                {% endif %} 

            </div>
            <div class="section-body">
                {% if ("body" in data[section] and "heading" in data[section]) or section == "title" %}
                    {% if data["result"]["section_issue"]["not_found"] == [] and data["result"]["section_issue"]["sequence"] == [] and data[section]["body"] == {} and data[section]["heading"] == {} %}
                        <p>This section has proper formatting and sequence. </p>
                    {% else %}  
                        <p>Multiple paragraphs in this section have incorrect styling.</p>
                    {% endif %}

                    {% for key, value in data[section]["body"].items() %}
                        
                        <div class="reference-item">
                            <strong>Paragraph {{key}}:</strong> 
                                {% if value["paragraph_issues"] != {} %}
                                    {{value["paragraph_issues"]["style"]}} &nbsp;
                                {% endif %}
                                {% if value["run_issues"] != [] %}
                                    Make sure the font size, bold, and italic is correct
                                {% endif %}
                        </div>

                    {% endfor %}
                {% else %} <!-- WIP -->
                    <p>This section has proper formatting and sequence. </p>
                {% endif %}
            </div>
        </div>
        {% endif %}
    {% endfor %}
    </div>

    <div>
        {{ data["novelty"] }}
    </div>

    <div>
        {{ data["semantic"] }}
    </div>

    <script>
        // Calculate actual statistics
        document.addEventListener('DOMContentLoaded', function() {
            // You could add JavaScript here to make the dashboard interactive
            // For example, to filter sections by issue type or severity
        });
    </script>
</body>
</html>

"""