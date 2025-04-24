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
            display: flex;
            justify-content: space-between;
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
        }
        .section-header {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
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
            display: flex;
            gap: 20px;
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
                <div class="stat-label">Total Issues</div>
                <div class="stat-value">{{ total_issues }}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Sequence Issues</div>
                <div class="stat-value">{{ sections_with_sequence_issues }}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Style Issues</div>
                <div class="stat-value"> {{ sections_with_style_issues }} </div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Missing Sections</div>
                <div class="stat-value"> {{ sections_with_not_found_issues }} </div>
            </div>
        </div>
    </div>

    <div class="dashboard">
        <!-- Structure Issues Section -->

        <!-- Title Section -->
        <div class="section-card">
            <div class="section-header">
                Title

                {% if data["title"]["section_issue"]["not_found"] == [] and data["title"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["title"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 

            </div>
            <div class="section-body">

                {% if data["title"]["section_issue"]["not_found"] == [] and data["title"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper formatting and sequence.</p>
                {% endif %}  

                {% if data["title"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Title section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["title"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["title"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["title"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
                
            </div>
        </div>

        <!-- Authors Section -->
        <div class="section-card">
            <div class="section-header">
                Authors
                {% if data["authors"]["section_issue"]["not_found"] == [] and data["authors"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["authors"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">

                {% if data["authors"]["section_issue"]["not_found"] == [] and data["authors"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["authors"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Authors section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["authors"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["authors"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["authors"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}

            </div>
        </div>

        <!-- Abstract Section -->
        <div class="section-card">
            <div class="section-header">
                Abstract
                {% if data["abstract"]["section_issue"]["not_found"] == [] and data["abstract"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["abstract"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["abstract"]["section_issue"]["not_found"] == [] and data["abstract"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["abstract"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Abstract section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["abstract"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["abstract"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["abstract"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>

        <!-- Introduction Section -->
        <div class="section-card">
            <div class="section-header">
                Introduction
                {% if data["introduction"]["section_issue"]["not_found"] == [] and data["introduction"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["introduction"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["introduction"]["section_issue"]["not_found"] == [] and data["introduction"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["introduction"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Introduction section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["introduction"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["introduction"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["introduction"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>

        <!-- Methods Section -->
        <div class="section-card">
            <div class="section-header">
                Methods
                {% if data["method"]["section_issue"]["not_found"] == [] and data["method"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["method"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["method"]["section_issue"]["not_found"] == [] and data["method"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["method"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Method section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["method"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["method"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["method"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>

        <!-- Literature Review Section -->
        {% if "literature_review" in data %}
            <div class="section-card">
                <div class="section-header">
                    Literature Review
                    {% if data["literature_review"]["section_issue"]["not_found"] == [] and data["literature_review"]["section_issue"]["sequence"] == [] %}
                        <span class="status-tag status-pass">No Issues</span>
                    {% endif %}       

                    {% if data["literature_review"]["section_issue"]["sequence"] != [] %}
                        <span class="status-tag status-warning">Sequence Issue</span>
                    {% endif %} 
                </div>
                <div class="section-body">
                    {% if data["literature_review"]["section_issue"]["not_found"] == [] and data["literature_review"]["section_issue"]["sequence"] == [] %}
                        <p>This section has proper author information, affiliations, and email addresses.</p>
                    {% endif %}  

                    {% if data["literature_review"]["section_issue"]["sequence"] != [] %}
                        <p>This section has a sequence issue related to the Literature Review section.</p>
                        <ul class="issue-list">
                            <li class="issue-item sequence">{{ data["literature_review"]["section_issue"]["sequence"][0] }}</li>
                        </ul>
                    {% endif %}
                </div>
            </div>
        {% endif %}

        <!-- Results Section -->
        <div class="section-card">
            <div class="section-header">
                Result
                {% if data["result"]["section_issue"]["not_found"] == [] and data["result"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["result"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["result"]["section_issue"]["not_found"] == [] and data["result"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["result"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Result section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["result"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["result"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["result"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>

        <!-- Discussion Section -->
        <div class="section-card">
            <div class="section-header">
                Discussion
                {% if data["discussion"]["section_issue"]["not_found"] == [] and data["discussion"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["discussion"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["discussion"]["section_issue"]["not_found"] == [] and data["discussion"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["discussion"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Discussion section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["discussion"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["discussion"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["discussion"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>

        <!-- Conclusion Section -->
        <div class="section-card">
            <div class="section-header">
                Conclusion
                {% if data["conclusion"]["section_issue"]["not_found"] == [] and data["conclusion"]["section_issue"]["sequence"] == [] %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["conclusion"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 
            </div>
            <div class="section-body">
                {% if data["conclusion"]["section_issue"]["not_found"] == [] and data["conclusion"]["section_issue"]["sequence"] == [] %}
                    <p>This section has proper author information, affiliations, and email addresses.</p>
                {% endif %}  

                {% if data["conclusion"]["section_issue"]["sequence"] != [] %}
                    <p>This section has a sequence issue related to the Conclusion section.</p>
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["conclusion"]["section_issue"]["sequence"][0] }}</li>
                    </ul>
                {% endif %}

                {% if data["conclusion"]["section_issue"]["not_found"] != [] %}
                    <ul class="issue-list">
                        <li class="issue-item sequence">{{ data["conclusion"]["section_issue"]["not_found"][0] }}</li>
                    </ul>
                {% endif %}
            </div>
        </div>
        
        <!-- References Section -->
        <div class="section-card">
            <div class="section-header">
                References
                {% if data["references"]["section_issue"]["not_found"] == [] and data["references"]["section_issue"]["sequence"] == [] and data["references"]["body"] == {} and data["references"]["heading"] == {} %}
                    <span class="status-tag status-pass">No Issues</span>
                {% endif %}       

                {% if data["references"]["section_issue"]["sequence"] != [] %}
                    <span class="status-tag status-warning">Sequence Issue</span>
                {% endif %} 

                {% if data["references"]["body"] != {} or data["references"]["heading"] != {}  %}
                    <span class="status-tag status-error"> {{ data["references"]["body"] | length + data["references"]["heading"] | length}} Style Issues</span>
                {% endif %} 

            </div>
            <div class="section-body">
                <p>Multiple paragraphs in this section have incorrect styling.</p>
                <div class="references-issues">

                    {% for key, value in data["references"]["body"].items() %}
                        <div class="reference-item">
                            <strong>Paragraph {{key}}:</strong> {{value["paragraph_issues"]["style"]}}
                        </div>
                    {% endfor %}

                </div>
            </div>
        </div>

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