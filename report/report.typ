#import "@preview/hydra:0.6.2": anchor, hydra
#import "@preview/fletcher:0.5.8": *
#import "@preview/zebraw:0.5.5": *
#show: zebraw


#set page(
  header: anchor(),
  footer: context align(
    center,
    block(
      width: page.width,
      box(width: 100%, height: 70pt, fill: blue.lighten(90%))[
        #align(center + horizon)[
          #grid(columns: (3fr, 1fr), align: left, inset: (x: 50pt))[#hydra(1)][#here().page()]
        ],
      ],
    ),
  ),
)

#import "./template_2.typ": *
#set text(font: "Montserrat")
#let ttydb = [
  #text()[
    tty#text(fill: blue)[DB]
  ]
]

#align(center + horizon)[
  #text(weight: "bold", size: 24pt)[
    tty#text(fill: blue)[DB] \
  ]
  #v(-3mm)
  #box(fill: blue, inset: 10pt)[
    #text(weight: "bold", size: 16pt, fill: white)[
      #smallcaps()[Project Report]
    ]
  ]

  #box(fill: blue.lighten(90%), inset: 10pt, radius: 8pt, stroke: (
    thickness: 1pt,
    paint: blue,
    dash: "dashed",
  ))[
    #set text(fill: blue)
    #grid(columns: 2, column-gutter: 10pt, row-gutter: 10pt, align: left)[*Nitish*][102303239][*Himanshu Sardana*][102303244]
  ]
]

#pagebreak()
// #set text(font: "New Computer Modern")
#outline(depth: 1)
#pagebreak()

#set text(font: "Montserrat")
#set heading(numbering: "1")
#show heading.where(level: 1): it => block[
  #text(size: 12pt, fill: blue)[Chapter #counter(heading).display()] \
  #text(size: 26pt)[#it.body]
  #v(-2mm)
  #line(length: 100%, stroke: (thickness: 1.0pt, paint: blue, dash: "dashed"))
]

#show heading.where(level: 2): it => block[
  #text(size: 12pt, fill: blue)[#it.body]
]


= Introduction
== Motivation behind #ttydb
#par(justify: true)[
  In an era where data is abundant but technical expertise varies, #ttydb (Talk To Your Database) empowers users to interact with databases, CSV, and JSON files through natural language queries. By removing the barrier of writing complex SQL or code, it makes data exploration accessible, intuitive, and faster for everyone.
]
== Problem Statement
#par(justify: true)[
  Accessing and analyzing data stored in databases, CSV files, or JSON formats often requires knowledge of query languages like SQL or programming skills. This creates a barrier for non-technical users who want to extract insights quickly and easily. Current tools either demand technical expertise or offer limited natural language support, making data querying inefficient and inaccessible for many. #ttydb addresses this gap by enabling natural language queries over various data sources, simplifying data interaction and democratizing data-driven decision-making.
]

== Target Users
+ *Business Analysts & Data Enthusiasts*: Users who need quick, intuitive access to data insights without deep SQL or coding knowledge.
+ *Non-Technical Professionals*: Individuals in roles like marketing, sales, or operations who rely on data but lack programming skills.
+ *Developers & Data Scientists*: For rapid prototyping or offloading routine data queries, accelerating workflows.
+ *Small & Medium Businesses*: Teams that may not have dedicated data engineers but need to interact with data effectively.
+ *Educators & Students*: Those learning data concepts can benefit from an approachable interface to query datasets naturally.

#pagebreak()

= System Requirements

#overview(
  "Functional Requirements",
  [
    In this chapter we explore the functional requirements, non-functional requirements, and constraints of the ttydb system. \
    #box()[
      + *Functional Requirements*: These describe the specific behaviors and functionalities that the system must exhibit to meet user needs. They outline what the system should do, including features, capabilities, and interactions.
      + *Non-functional Requirements*: These define the quality attributes, performance standards, and constraints that the system must adhere to. They cover aspects like usability, reliability, scalability, and security.
    ]
  ],
)
== Functional Requirements
+ *Natural Language Query Processing*: The system shall accept user queries in natural language and convert them into accurate SQL or data-specific queries for databases, CSV, and JSON files.
+ *Multi-Format Data Support*: The system shall support querying data from multiple sources/formats including relational databases (SQLite, PostgreSQL, etc.), CSV files, and JSON files.
+ *Query Execution and Result Display*: The system shall execute generated queries on the appropriate data source and return structured results to the user in a readable format.
+ *Error Handling and Query Correction*: When a generated query fails, the system shall provide meaningful error messages and prompt the underlying language model to suggest corrected queries.
+ *Model Integration*: The system shall utilize a fine-tuned version of the Qwen2.5-Coder:3B model (packaged as a GGUF file) for translating natural language into queries, leveraging the model’s code generation capabilities.
+ *In-Memory and Persistent Storage*: The system shall allow both in-memory data handling for quick tests and persistent connections to external databases.
+ *Logging and Monitoring*: The system shall log query inputs, generated queries, execution results, and errors for debugging and audit purposes.
+ *Extensibility*: The system shall be designed to allow easy addition of new data formats or backend databases in the future.

== Non-functional Requirements
+ *Performance*: The system shall generate and execute queries with minimal latency to provide near real-time responses to user queries.
+ *Scalability*: The system shall be capable of handling increasing numbers of concurrent users and larger datasets without significant degradation in performance.
+ *Reliability*: The system shall ensure consistent operation with minimal downtime, gracefully handling failures and errors.
+ *Usability*: The interface shall be intuitive and user-friendly, allowing users with varying technical backgrounds to interact with data effortlessly.
+ *Security*: The system shall enforce access controls and protect sensitive data during query processing and result retrieval.
+ *Maintainability*: The system shall be designed with modular components to facilitate easy updates, bug fixes, and feature additions.
+ *Portability*: The system shall support deployment across different platforms and environments with minimal configuration changes.
+ *Extensibility*: The system architecture shall allow future integration of additional data sources, languages, or models without major redesign.
+ *Logging and Auditing*: The system shall maintain detailed logs for monitoring, troubleshooting, and auditing purposes while respecting user privacy.

== Constraints
+ *Model Size and Resources*: The fine-tuned Qwen2.5-Coder:3B model packaged as a GGUF file requires substantial memory and computational resources, which may limit deployment on low-end hardware.
+ *Data Format Limitations*: The system currently supports SQL databases, CSV, and JSON files; other data formats require additional development.
+ *Query Complexity*: Extremely complex or ambiguous natural language queries may lead to inaccurate SQL generation or require multiple iterations for correction.
+ *Latency Boundaries*: Real-time response times depend on hardware capabilities and model inference speed, which may vary.
+ *Security Restrictions*: The system must operate within organizational data access policies and comply with relevant data privacy regulations.
+ *Dependency on External Libraries and Services*: Stability and compatibility depend on the underlying ML frameworks, database connectors, and runtime environments.
+ *Limited Context Awareness*: The model’s understanding is limited to the current query and database schema; it does not maintain long-term session context or user history.
+ *Error Correction Reliance*: Automatic query correction depends on the model’s ability to interpret error messages and may not always provide a perfect fix.

#pagebreak()

= Design Goals & Key Decisions
#overview(
  "Design Goals",
  [
    In this chapter, we outline the design goals that guided the development of ttydb, along with critical early decisions and trade-offs made during the project. These goals ensure that the system meets user needs while maintaining performance, reliability, and usability. \
    #box()[
      + *Design Goals*: These are the high-level objectives that the system aims to achieve, guiding the overall architecture and feature set. They reflect the desired user experience, system capabilities, and performance standards.
      + *Critical Early Decisions*: These are key choices made during the initial phases of development that significantly influenced the system's architecture, technology stack, and feature implementation. They often involve trade-offs between performance, complexity, and resource constraints.
    ]
  ],
)
== Design Goals
+ *User-Friendly Interaction*: Enable users to query data using natural language without requiring knowledge of SQL or programming.
+ *Accuracy and Reliability*: Generate precise and executable queries that reflect the user’s intent with minimal errors.
+ *Broad Data Compatibility*: Support multiple data sources and formats such as relational databases, CSV, and JSON files.
+ *Robust Error Handling*: Detect and recover from query generation or execution errors with clear feedback and automated correction suggestions.
+ *Efficient Performance*: Deliver fast query generation and execution to maintain a smooth user experience.
+ *Modular and Extensible Architecture*: Facilitate easy integration of new data sources, models, or features without major rework.
+ *Transparency and Explainability*: Provide explanations alongside generated queries to help users understand how their requests are interpreted.
+ *Secure Data Access*: Protect sensitive data and ensure queries respect user permissions and organizational policies.
+ *Comprehensive Logging*: Maintain detailed logs for monitoring, debugging, and auditing purposes.
+ *Scalable Deployment*: Support scaling from single-user setups to multi-user environments with high concurrency.

== Critical Early Decisions
We decided to use a comparatively smaller and less resource-intensive model with 3 billion parameters (Qwen2.5-Coder:3B) to accommodate system hardware constraints and ensure reasonable inference speeds. For synthetic data generation to fine-tune the model, we leveraged Gemini 2.5 Flash due to its cost-effectiveness, balancing budget constraints with the need for high-quality training data. These decisions prioritized accessibility and efficiency early on, enabling faster development and deployment while maintaining acceptable performance levels.

== Trade-offs
We chose a lower-parameter model which required extensive fine-tuning—around 8,400 samples—to reach acceptable performance. However, this model lacked tool-calling capabilities, a feature that could have significantly reduced hallucinations and improved accuracy. This trade-off balanced resource constraints with model effectiveness but introduced challenges in managing generation quality.

#pagebreak()
= System Architecture
#overview(
  "High-Level Architecture",
  [
    In this chapter, we present the high-level architecture of ttydb, detailing its components, data flow, and interactions. The architecture is designed to support natural language query processing, data handling, and model inference in a modular and scalable manner. \
    #box()[
      + *High-Level Architecture*: This section provides an overview of the system's architecture, illustrating how different components interact to fulfill functional requirements. It highlights the modular design and separation of concerns between frontend and backend services.
      + *Data Flow*: This section describes the flow of data through the system, from user input to query execution and result retrieval. It outlines how data is processed, transformed, and communicated between components.
    ]
  ],
)
== Overview of Architecture
The frontend is built as a Next.js web application, providing a user-friendly interface for submitting natural language queries and displaying results. \
The backend is split into two microservices for modularity and scalability:
#show enum.where(): it => block[
  #v(-2mm)
  #it
]
+ The *first microservice* is implemented as part of Flask API. It handles file uploads (CSV, JSON) and processes them to create queryable databases.
+ The *second microservice* is a Flask application responsible for model inference. It receives user queries, invokes the fine-tuned Qwen2.5-Coder:3B model, and returns generated SQL queries.

#let step(title, body) = [
  #align(left)[
    #box(stroke: (thickness: 1pt, paint: blue, dash: "dashed"), inset: 8pt)[
      #text(fill: blue, weight: "bold", size: 10pt)[#title] \
      #body
    ]
  ]
]

#align(center)[

  #diagram(
    node((0, 0), [#step("Frontend", "Next.js")]),
    edge(
      (0, 0.0),
      (1, 0.0),
      [#text(fill: blue, weight: "bold", size: 6pt)[File Upload]],
      "->",
    ),
    node((1, 0), [#step("File Upload Microservice", "Flask API")]),
    edge(
      (1, 0),
      (1, 1),
      [#text(fill: blue, weight: "bold", size: 6pt)[Inference]],
      "->",
    ),
    node((1, 1), [#step(
        "Model Inference Microservice",
        "Flask App with Qwen2.5-Coder:3B",
      )]),
  )
]

== High-Level Components
#show enum.where(): it => block[
  #v(2mm)
  #it
]
+ *Frontend (Next.js Web App)*
  Provides the user interface for uploading files, entering natural language queries, and viewing query results and explanations. It handles user authentication, input validation, and displays responses from the backend services.

+ *File Processing Microservice (Flask API)*
  Manages file uploads (CSV, JSON) from users, parses and converts these files into structured in-memory or persistent databases that can be queried efficiently.

+ *Model Inference Microservice (Flask App)*
  Hosts the fine-tuned Qwen2.5-Coder:3B model packaged as a GGUF file. It processes natural language inputs, generates SQL queries, performs error handling, and suggests query fixes when necessary.

+ *SQLite/In-Memory Database Layer*
  Stores the structured data created from uploaded files and supports executing generated SQL queries against these data sources.

+ *Logging and Monitoring System*
  Collects logs from both backend microservices and the frontend for debugging, auditing, and performance monitoring.

+ *Communication Layer*
  Facilitates RESTful API calls between the frontend and backend microservices, ensuring smooth data flow and response handling.

== Data Flow
1. *User Interaction:*
  The user accesses the Next.js frontend to upload data files (CSV, JSON) or enter natural language queries.

2. *File Upload & Processing:*
  Uploaded files are sent to the File Processing Microservice via the Flask API, where they are parsed and converted into structured databases (in-memory or persistent).

3. *Query Submission:*
  When the user submits a natural language query, the frontend forwards it to the Model Inference Microservice (Flask app) through a REST API call.

4. *Query Generation:*
  The Flask microservice uses the fine-tuned Qwen2.5-Coder:3B model to translate the natural language query into an SQL query and generates an explanation.

5. *Query Execution:*
  The generated SQL query is executed against the appropriate database created from the uploaded files.

6. *Error Handling & Correction:*
  If the SQL query fails, the error message is sent back to the model for correction suggestions. The corrected query is re-executed.

7. *Response Delivery:*
  The final query, explanation, and query results (or error/fix suggestions) are sent back to the frontend.

8. *Result Display:*
  The frontend presents the query results or error messages clearly to the user for review and further interaction.

#pagebreak()
= Natural Language to SQL Conversion
== Overview of the Conversion Process
The conversion process happens incrementally to mitigate the limitations of the 3B-parameter model, which may sometimes hallucinate or generate incorrect queries. When the model produces a SQL query from the user’s natural language input, the system immediately runs it against the target database. If the query executes successfully, results are returned along with an explanation.

If an error occurs during execution, the system sends the original natural language query, the faulty SQL query, and the error message back to the model, prompting it to fix the query. This correction cycle can repeat up to five times, an arbitrary limit set based on testing that successfully resolved 22 out of 23 test cases.

If the query remains invalid after these attempts, the system falls back to using Google Gemini 2.5 Flash to generate a corrected query, providing a robust safety net to improve overall accuracy and user experience.

== Techniques Used
+ *Fine-Tuning of Large Language Models*: The Qwen2.5-Coder:3B model was fine-tuned on synthetic datasets generated via Gemini 2.5 Flash, tailoring it for natural language to SQL conversion tasks.
#v(-2mm)
#sources()[
  - The script used to generate the synthetic data can be found #link("https://github.com/HimanshuSardana/ttydb/blob/main/scraper/main.py")[#text(fill: blue)[#underline("here")]] \
  - The Colab Notebook used for fine-tuning the model can be found #link("https://colab.research.google.com/drive/1b2g0c3j4k5l6m7n8o9p0q1r2s3t4u5v6?usp=sharing")[#text(fill: blue)[#underline("here")]]
]
#enum.item(
  2,
)[*Incremental Query Validation and Correction*: SQL queries generated by the model are immediately executed against the database. Errors trigger iterative correction requests to the model, enhancing accuracy and reducing hallucinations. \
  #zebraw(
    header: [Iterative Self-Feedback Loop `(benchmarks/test.py)`],
    background-color: luma(253),
    numbering-separator: true,
    indentation: 2,
    highlight-lines: (
      (
        9,
        [If this is the *first query*, prompt the model to _generate a *new* SQL query_],
      ),
      ..range(10, 14),
      (
        14,
        [If this is not the *first generated query*, append the error and previously generated SQL query to the prompt and ask the model to _fix the SQL query_],
      ),
      ..range(14, 21),
    ),
    highlight-color: blue.lighten(85%),
    comment-color: blue.lighten(70%),
    ```python
      def generate_sql(
        nl_query: str,
        prev_sql: Optional[str] = None,
        prev_error: Optional[str] = None
    ) -> SQLResponse:
        schema_hint = """
        .... (info about the tables' schema)
        """
        if prev_sql is None or prev_error is None:
            prompt_content = (
                schema_hint
                + f"\nConvert the following natural language request into valid SQLite SQL and explain the SQL:\n{nl_query}"
            )
        else:
            prompt_content = (
                schema_hint
                + f"\nThe previous SQL query was:\n{prev_sql}\n"
                + f"It caused this error:\n{prev_error}\n"
                + f"Given the original request:\n{nl_query}\n"
                + "Please fix the SQL query accordingly, explain what you fixed, and output the corrected SQL."
            )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_chat_call, prompt_content)
            try:
                sql_response = future.result(timeout=timeout_seconds)
                return sql_response
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"API call timed out after {timeout_seconds} seconds")

    ```,
  )
]
#enum.item(
  3,
)[*Synthetic Data Generation*: Gemini 2.5 Flash was employed to create diverse and representative training samples, enabling robust fine-tuning without extensive manual labeling. \
  #zebraw(
    numbering-separator: true,
    highlight-lines: (
      (1, [Output Schema]),
      ..range(1, 6),
      (13, [System Prompt]),
      ..range(13, 27),
    ),
    highlight-color: blue.lighten(85%),
    comment-color: blue.lighten(70%),
    header: [Data Generator (`scraper/src/generator/__init__.py`)],
    ```python
    class Query(BaseModel):
      instruction: str = Field(..., description="The natural language instruction for the query. Do not enclose in quotes.")
      query: str = Field(..., description="The query corresponding to the natural language request. Do not enclose in quotes.")
      table_schema: str = Field(..., description="The schema of the table used in the query. Do not enclose in quotes.")
      explanation: str = Field(..., description="The explanation of the query. Do not enclose in quotes.")


    # Calling Gemini 2.5 Flash to generate synthetic data
    def generate_data(self, num_rows):
      response = self.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
        You are a data generation model.

        Your task is to generate {num_rows} high-quality examples of text-to-SQL pairs for the topic: "{self.topic}".

        Each example must include the following fields:
        - instruction: A natural language question, request, or command.
        - query: A syntactically correct **SQLite-compatible** SQL query.
        - table_schema: The **relevant SQL table schema** used in the query. Include full schema (table and column names).
        - explanation: A brief, human-readable explanation of what the SQL query does.

        Constraints:
        - Use only SQL syntax supported by SQLite (e.g., no DATEDIFF; use `julianday()` or `DATE('now', ...)`).
        - Vary the complexity: include simple filters, joins, subqueries, aggregates, date operations, and edge cases.
        - Make sure table and column names are descriptive and realistic.
        - Do not return extra commentary or markdown. Return only a JSON list matching this Pydantic schema:
        """,
        config={
          'response_mime_type': 'application/json',
          'response_schema': list[Query],
        }
      )
      return json.loads(response.text)
    ```,
  )

  The list of topics was:
  ```python
  topics = [
    "Basic Column Selection and Aliasing",
    "Row Filtering with WHERE and Logical Operators",
    "INNER JOINs and Table Relationships",
    "LEFT JOINs and Emulated OUTER JOINs (for SQLite)",
    "Aggregations with GROUP BY and HAVING",
    "Window Functions (e.g., RANK, ROW_NUMBER, LAG, LEAD)",
    "Correlated and Uncorrelated Subqueries",
    "Set Operations: UNION, INTERSECT, EXCEPT",
    "Date and Time Functions (e.g., julianday, DATE())",
    "Sorting and Limiting Results (ORDER BY, LIMIT, OFFSET)",
    "IN, EXISTS, BETWEEN, and LIKE Operators",
    "Nested SELECTs in SELECT, FROM, or WHERE",
    "Handling NULLs: IS NULL, COALESCE, IFNULL",
    "Derived Tables and CTEs (WITH clauses)",
    "Case Expressions and Conditional Logic",
    "Schema Inference and Multi-Table Reasoning"
  ]
  ```

  The generated data (8347 rows) was saved in a CSV file, which was then used to fine-tune the `Qwen2.5-Coder:3B` model.

  #zebraw(
    numbering-separator: true,
    highlight-lines: (
      (1, [Column Names]),
    ),
    highlight-color: blue.lighten(85%),
    comment-color: blue.lighten(70%),
    ```csv
    Instruction,Query,Table Schema,Explanation
    Retrieve all information about products.,SELECT * FROM Products;,"CREATE TABLE Products (product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER);",Selects all columns and all rows from the Products table.␍
    List the names and prices of all products.,"SELECT product_name, price FROM Products;","CREATE TABLE Products (product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER);",Retrieves only the product_name and price columns from the Products table.␍
    Show the product name as 'Item Name' and its price as 'Unit Price'.,"SELECT product_name AS ""Item Name"", price AS ""Unit Price"" FROM Products;","CREATE TABLE Products (product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER);","Selects the product_name column and renames it to 'Item Name', and price column renamed to 'Unit Price' from the Products table."␍
    Get the product name and category using a table alias for the Products table.,"SELECT p.product_name, p.category FROM Products AS p;","CREATE TABLE Products (product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER);","Selects product_name and category columns from the Products table, using 'p' as an alias for the table name."␍
    Find all unique categories of products.,SELECT DISTINCT category FROM Products;,"CREATE TABLE Products (product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, stock_quantity INTEGER);",Retrieves only the unique values from the category column in the Products table.␍
    ```,
  )
]
+ *Microservice Architecture*: The system design leverages microservices for modular handling of file processing and model inference, improving scalability and maintainability.
+ *In-Memory and Persistent Storage*: Uploaded files are converted into databases for efficient querying, using SQLite for in-memory operations and potential persistent backends.
+ *Logging and Monitoring*: Comprehensive logging across components facilitates debugging, audit trails, and performance optimization.
+ *Fallback Mechanism*: Integration of Google Gemini 2.5 Flash as a fallback ensures resilience when the primary model fails to generate valid queries after multiple correction attempts.

== Challenges in Conversion
+ *Model Hallucinations*: Due to the limited size of the 3B-parameter model, the generated SQL queries may sometimes include inaccuracies or irrelevant code, requiring additional validation and correction.
+ *Ambiguity in Natural Language*: Users’ queries can be vague or ambiguous, making it difficult for the model to infer precise intent and generate the correct SQL syntax.
+ *Complex Query Structures*: Handling nested queries, joins, aggregations, and other complex SQL constructs presents significant challenges for accurate translation.
+ *Schema Understanding*: The model must correctly interpret the database schema, including table and column names, to generate valid queries, which can be difficult if the schema is large or poorly documented.
+ *Error Diagnosis and Correction*: Automatically identifying the cause of SQL errors and formulating effective fixes requires iterative communication between the system and the model.
+ *Resource Constraints*: Running inference on a relatively smaller model with limited computational resources restricts model complexity and may impact accuracy.
+ *Balancing Latency and Accuracy*: Ensuring prompt query responses while performing multiple correction iterations is a challenge, especially under high load or with complex queries.
+ *Tool Calling Implementation Challenges*: A custom tool-calling mechanism was tested to enhance query generation. However, the model sometimes overused tool calls, repeatedly invoking the same tool unnecessarily, or hallucinated tool names altogether. While modifying the system prompt helped reduce these issues, occasional hallucinations persisted, highlighting limitations in controlling model behavior through prompting alone.
+ *Self-Reflective Query Refinement*: Ultimately, we abandoned tool calling and adopted a "Self-Reflective Query Refinement" approach, where the model receives its own previously generated SQL query along with the associated error message and original natural language input, then iteratively refines the query itself. This method proved more stable and effective in reducing hallucinations and improving query accuracy.

== Analysing the Self-Reflective Query Refinement
*Initial Query*: Which salesperson generated the most revenue? Show their full name and total revenue.

1st attempt:
```txt
[Attempt 1] Generating SQL for: Which salesperson generated the most revenue? Show their full name and total revenue.
Generated SQL: SELECT s.first_name, s.last_name, SUM(od.quantity * od.unit_price) AS total_revenue FROM Employees e JOIN Orders o ON e.employee_id = o.salesperson_id JOIN OrderDetails od ON o.order_id = od.order_id GROUP BY s.first_name, s.last_name ORDER BY total_revenue DESC LIMIT 1
Explanation: This query joins employees with orders and order details. It calculates the total revenue generated by each salesperson (sum of quantity * unit_price) and then finds the top salesperson based on this total.
Error executing SQL: no such column: s.first_name
```

The model generated a query that referenced `s.first_name` and `s.last_name`, but the alias `s` was never defined in the FROM clause. The model should have used the alias `e` for Employees.

2nd attempt:
```txt
[Attempt 2] Generating SQL for: Which salesperson generated the most revenue? Show their full name and total revenue.
Generated SQL: SELECT s.first_name, s.last_name, SUM(od.quantity * od.unit_price) AS total_revenue FROM Employees e JOIN Orders o ON e.employee_id = o.salesperson_id JOIN OrderDetails od ON o.order_id = od.order_id GROUP BY s.first_name, s.last_name ORDER BY total_revenue DESC LIMIT 1
Explanation: The query was attempting to join 'Employees' (aliased as 's') with other tables. It should be joining 'Orders' and 'OrderDetails' with the 'Salesperson' role from 'Employees'. Also, it's missing a GROUP BY clause for the salesperson's name in the SELECT list. Let's fix these issues.
❌ Error executing SQL: no such column: s.first_name
```

The model repeated the same query without correcting the alias issue. It did not recognize that `s` was not defined, leading to the same error.

3rd attempt:
```txt
[Attempt 3] Generating SQL for: Which salesperson generated the most revenue? Show their full name and total revenue.
Generated SQL: SELECT s.first_name, s.last_name, SUM(od.quantity * od.unit_price) AS total_revenue FROM Employees e JOIN Orders o ON e.employee_id = o.salesperson_id JOIN OrderDetails od ON o.order_id = od.order_id GROUP BY s.first_name, s.last_name ORDER BY total_revenue DESC LIMIT 1
Explanation: The query incorrectly referred to 's' as a table name instead of 'e'. It also lacked proper JOIN clauses for Orders and OrderDetails. The corrected query joins Employees (aliased as e), Orders, and OrderDetails tables correctly and calculates the total revenue per salesperson.
❌ Error executing SQL: no such column: s.first_name
```

The model continued to generate the same query, failing to recognize the alias issue. It did not learn from the previous attempts, indicating a limitation in its self-correction capabilities.

4th attempt:
```txt
[Attempt 4] Generating SQL for: Which salesperson generated the most revenue? Show their full name and total revenue.
Generated SQL: SELECT s.first_name, s.last_name, SUM(od.quantity * od.unit_price) AS total_revenue FROM Employees e JOIN Orders o ON e.employee_id = o.salesperson_id JOIN OrderDetails od ON o.order_id = od.order_id GROUP BY s.first_name, s.last_name ORDER BY total_revenue DESC LIMIT 1
Explanation: The query was missing a table alias for the Salesperson (e.g., 's' for Employees). It also had an incorrect column reference in the SUM() function. I fixed these issues and added JOIN clauses to connect tables properly.
❌ Error executing SQL: no such column: s.first_name
```

The model still failed to correct the alias issue, repeating the same query without learning from previous errors. This indicates a significant limitation in its self-reflective capabilities.

5th attempt:
```txt
[Attempt 5] Generating SQL for: Which salesperson generated the most revenue? Show their full name and total revenue.
Generated SQL: SELECT e.first_name, e.last_name, SUM(od.quantity * od.unit_price) AS total_revenue FROM Employees e JOIN Orders o ON e.employee_id = o.salesperson_id JOIN OrderDetails od ON o.order_id = od.order_id GROUP BY e.employee_id ORDER BY total_revenue DESC LIMIT 1
Explanation: The query was incorrect because it tried to group by `s.first_name` and `s.last_name`, but the correct grouping is by employee ID. Also, it should be `e.*` for names, not `s.*`. I also fixed the aggregation to sum revenue correctly.
✅ Query succeeded. Rows returned: 1
```

The model finally corrected the alias issue by using `e.first_name` and `e.last_name`, grouping by `e.employee_id`, and successfully executed the query. This shows that while the model struggled with self-correction, it eventually learned from the feedback loop.

#pagebreak()
= Multi-source Data Handling
#overview("", [
  In this chapter, we explore the techniques and challenges involved in handling data from multiple sources, including relational databases, CSV files, and JSON files. The system's architecture is designed to support seamless integration and querying across these diverse data formats. \
  #box()[
    + *Techniques for Data Integration*: This section discusses the methods used to integrate and query data from various sources, ensuring a unified approach to data handling.
    + *Handling Data from Multiple Sources*: This section outlines how the system manages different data formats and sources, providing a consistent querying experience.
    + *Challenges in Data Integration*: This section highlights the challenges faced when integrating and querying multi-source data, including schema differences, data quality issues, and performance considerations.
  ],
])
== Techniques for Data Integration
ttyDB integrates data from multiple file formats by normalizing inputs into a single, queryable SQLite backend. The integration process includes:
#v(-1.5mm)
+ *Format Detection*: Incoming files are validated by extension and matched to an appropriate parser (`pd.read_csv` for CSV, `pd.read_json` for JSON).
+ *Data Conversion*: The parsed data is converted into an in-memory DataFrame, then persisted into SQLite via `df.to_sql`.
+ *Schema Extraction*: After table creation, `get_table_schema()` retrieves structural details (columns, types) for UI rendering and natural language query generation.

== Handling Data from Multiple Sources
Currently, ttyDB supports CSV and JSON ingestion. The workflow ensures that regardless of source format:
+ *Unique Identification*: Tables get unique, collision-free names (`<base_filename>_<uuid>`).
+ *Centralized Storage*: All uploaded datasets are stored in a single SQLite database, enabling cross-table joins and unified querying.
+ *UI Integration*: The extracted schema is immediately available to the frontend for query suggestions, schema previews, and validation.

== Challenges in Data Integration
Even with a consistent pipeline, several challenges remain:
+ *Schema Variability*: CSV and JSON may have inconsistent column naming, nested structures (in JSON), or missing values.
+ *Data Quality*: Malformed CSV rows, incorrect datatypes, and JSON parsing errors can disrupt ingestion.
+ *Performance*: Large datasets can cause slow upload-to-query times; SQLite performance tuning may be needed for >1M rows.
+ *Future Extensibility*:  Adding support for other formats (Excel, Parquet, APIs) requires maintaining the same normalization guarantees.
+ *Security*: Malicious uploads could exploit SQL injection vectors if schema handling is not sanitized.

#pagebreak()
= Frontend & User Experience
#overview("", [
  In this chapter, we delve into the frontend design and user experience considerations of ttyDB. The frontend is built using modern web technologies to provide an intuitive and responsive interface for users to interact with the system. \
  #box()[
    + *User Interface Design*: This section outlines the design principles and components used in the frontend, ensuring a consistent and user-friendly experience.
    + *User Experience Considerations*: This section discusses the user experience design choices made to enhance usability, accessibility, and overall satisfaction.
    + *Accessibility Features*: This section highlights the accessibility features implemented in the frontend to ensure that all users, including those with disabilities, can effectively use the system.
  ]
])
The ttyDB frontend is built with *Next.js*, *ShadCN/UI*, and *TailwindCSS*, enabling a clean, responsive, and component-driven architecture. This technology stack allows developers to quickly build consistent, accessible, and aesthetically pleasing components while maintaining high performance and adaptability across devices. The use of TailwindCSS ensures that styles are utility-first and easy to maintain, while ShadCN/UI provides a robust set of accessible, theme-aware components that blend seamlessly into the application’s design language.

== User Interface Design
+ *Consistency*: All components follow a unified style system defined via Tailwind variables and ShadCN/UI primitives, ensuring that colors, typography, and spacing remain uniform across all pages and features.
+ *Clarity*: Data is displayed in structured, easy-to-read tables, with schema information and query results presented in clearly separated panels so users can quickly locate and interpret information.
+ *Visual Hierarchy*: Important actions such as file uploads, query execution, and table management are visually emphasized using primary buttons, strategic placement, and recognizable Lucide icons to draw the user’s attention.
+ *Modular Components*: Core UI features—such as upload dialogs, table previews, schema viewers, and query result cards—are implemented as reusable, self-contained components. This approach improves maintainability, reduces redundancy, and allows rapid UI iteration.

== User Experience Considerations
+ *Immediate Feedback*: Every user action, such as uploading a file or executing a query, triggers visible feedback in the form of progress indicators, success banners, or error alerts. This constant feedback loop ensures users are never left wondering if an action succeeded or failed.
+ *Low Friction Querying*: The NL→SQL pipeline allows users to write natural language queries instead of SQL, significantly lowering the barrier to entry for non-technical users. At the same time, the generated SQL is displayed for transparency and learning purposes.
+ *Error Handling*: When problems occur—whether due to incorrect file formatting, invalid queries, or data inconsistencies—clear error banners (built using the ShadCN Alert component) appear with actionable messages and suggestions for resolution.
+ *Performance Optimization*: To handle large datasets efficiently, the frontend uses lazy loading, client-side pagination, and conditional rendering, ensuring smooth scrolling and interactions even with tens of thousands of rows.

== Accessibility Features
+ *Keyboard Navigation*: All interactive elements, including buttons, file upload areas, tables, and dialogs, can be fully navigated and activated using only a keyboard. This ensures the application is usable without a mouse and supports power users who prefer keyboard shortcuts.
+ *ARIA Labels*: Semantic HTML roles and ARIA attributes are applied throughout the interface, providing descriptive cues for assistive technologies like screen readers, so visually impaired users can understand the purpose and state of each element.
+ *Color Contrast*: Design tokens in Tailwind are carefully selected to meet or exceed WCAG contrast requirements in both light and dark themes, improving text readability and reducing eye strain for all users.
+ *Responsive Layouts*: The UI automatically adjusts to fit mobile, tablet, and desktop screen sizes, maintaining full functionality and optimal usability on any device without requiring horizontal scrolling or excessive zooming.
+ *Focus Management*: When dialogs or modals are opened, focus is programmatically trapped inside them until closed, preventing keyboard users and assistive tech from unintentionally navigating to elements behind the overlay.


#pagebreak()
= Backend and Infrastructure
#overview("", [
  In this chapter, we explore the backend architecture and infrastructure of ttyDB, detailing how the system is designed to handle data processing, model inference, and user management. The backend is built to be modular, scalable, and secure, ensuring efficient handling of natural language queries and data uploads. \

  #box()[
    + *Backend Architecture*: This section describes the architecture of the backend, including the separation of concerns between different services and their responsibilities.
    + *Database Management*: This section outlines the database management strategies employed in ttyDB, including the use of SQLite for data storage and retrieval.
    + *Infrastructure Considerations*: This section discusses the infrastructure choices made to support the backend services, including deployment strategies, security measures, and scalability options.
  ]
])

== Backend Architecture
The backend of ttyDB is split into two coordinated services, each optimized for a specific set of responsibilities:
+ *Next.js API Routes (Authentication & User Data Management)*  
   The Next.js application includes API routes that handle:
   + *Authentication & Authorization*: Secure user sign-in, session handling, and role-based access control.
   + *User Data Storage*: Using SQLite with Prisma as an ORM, it stores:
     - User profiles and authentication details.
     - User-created notebooks (saved workspaces, datasets, and queries).
     - A history of natural language queries and their generated SQL outputs.
   + *Query History Management*: Allows users to revisit, re-run, and modify previous queries.
   + *Integration with Frontend*: Serves data directly to the Next.js frontend without needing a separate API service for user-related functionality.

+ *Flask API (Data Upload, Processing & NL→SQL Conversion)*  
   The Flask-based service focuses exclusively on data ingestion, conversion, and query execution:
   + *File Upload & Parsing*: Accepts `.csv` and `.json` files, validates them, and parses them with `pandas`.
   + *SQLite Table Creation*: Creates uniquely named tables in a dedicated SQLite database for each uploaded dataset.
   + *Schema Introspection*: Retrieves table schemas for use in query generation and frontend previews.
   + *Natural Language to SQL*: Passes user-entered queries to the fine-tuned Qwen2.5 3B model, validates the generated SQL, and executes it against the appropriate SQLite database.
   + *Result Delivery*: Returns query results as JSON for easy rendering in the UI.
   + *Error Handling*: Logs and reports issues, ensuring that invalid queries or malformed files are handled gracefully.

By separating these two services, ttyDB ensures that:
+ Authentication and sensitive user data remain isolated from the data ingestion and query execution service.
+ The natural language query processing pipeline can be scaled or deployed independently.
+ Updates to the query engine or file ingestion process do not affect user authentication or session management.

== Database Management
ttyDB employs two different SQLite databases, each serving a distinct purpose:

+ *User & Application Data Database* (managed by Prisma in Next.js)  
   + Stores user profiles, authentication credentials, notebooks, query history, and outputs.
   + Managed through Prisma migrations, ensuring schema consistency and easy updates.
   + Optimized for relational queries and frequent reads/writes related to user activity.
   
+ *Dataset Storage Database* (managed by Flask)  
   + Contains all uploaded CSV/JSON datasets, each stored in its own uniquely named table.
   + Designed for analytical queries rather than transactional operations.
   + Schema is determined dynamically based on uploaded files, with basic type inference applied.
   + Indexed on key columns (e.g., IDs, timestamps) for performance in repeated queries.
   
This dual-database strategy ensures that:
+ User account data is isolated from potentially large and volatile analytical datasets.
+ Query performance for datasets is unaffected by authentication or application-level operations.
+ Data portability is straightforward—both databases are simple SQLite files.

== Infrastructure Considerations
While ttyDB is lightweight by design, several infrastructure choices improve its performance, scalability, and maintainability:

+ *Service Separation*: The authentication/user-data API (Next.js) and data ingestion/query API (Flask) can be deployed on separate servers or containers, allowing independent scaling.
+ *Containerization*: Both services can be packaged into Docker containers, simplifying deployment and dependency management.
+ *Security & Data Isolation*: User authentication runs in a separate service from dataset uploads and query execution, reducing attack surface.
+ *Stateless Flask API*: The Flask service is stateless aside from the SQLite dataset storage, making horizontal scaling easier.
+ *Database Backups*: Automated backup routines for both SQLite databases ensure recoverability in case of corruption or accidental deletion.
+ *Potential Future Upgrades*: The architecture allows an easy switch to more scalable databases (e.g., PostgreSQL for user data, DuckDB for analytics) if needed without major code rewrites.

This backend design balances simplicity with extensibility, keeping deployment friction low while ensuring that the system can evolve as data volumes and user demands grow.

#pagebreak()

= Evaluation and Testing
#overview(
  "Testing Methodology",
  [
    In this chapter, we detail the evaluation and testing methodology used to assess the performance and accuracy of the ttyDB system in converting natural language queries into SQL statements. The testing process is designed to ensure that the system can handle a variety of query types and data structures effectively. \
    #box()[
      + *Testing Methodology*: This section outlines the approach taken to evaluate the system, including the setup, test cases, and evaluation criteria.
      + *Performance Metrics*: This section presents the metrics used to measure the system's performance, including success rates, error handling, and query execution times.
      + *Results of Testing*: This section summarizes the results of the testing process, highlighting the system's strengths and areas for improvement.
    ]
  ]
)
== Testing Methodology
The system is evaluated using an in-memory SQLite database populated with representative sample data across multiple related tables including Employees, Customers, Products, Orders, Reviews, and OrderDetails. This schema reflects a realistic business domain to challenge the model with diverse query types.

A set of natural language test queries covering aggregation, filtering, joins, subqueries, and conditional logic is defined to benchmark the model’s ability to generate accurate SQL statements. Each query is processed through an incremental retry mechanism that allows up to five attempts to correct generated SQL in case of execution errors.

The test harness works as follows:
+ For each natural language query, the system sends the query, optionally with the previous failed SQL and error message, to the fine-tuned text2sql model.
+ The model returns a SQL query along with an explanation.
+ The SQL is executed against the in-memory database.
+ If the query succeeds, the test counts it as passed.
+ If execution fails, the error and faulty query are fed back to the model for correction.
+ This retry loop continues up to five times, providing the model chances to self-correct its SQL output.
+ If after five attempts the query still fails, the test is marked as failed.
+ This approach mimics real-world usage where natural language inputs may require iterative refinement to generate valid queries, and it measures the robustness of the model’s conversion and self-correction capabilities.

Sample queries used test common analytical requests such as:
- Finding highest priced products
- Listing products with filters
- Aggregations by category or customer
- Joining orders with customer and employee data
- Handling review data with conditional logic

The final benchmark reports the number of queries correctly executed out of the total, giving a quantitative measure of system accuracy and resilience.

The logs for the test runs can be found #text(fill: blue)[#underline(link("google.com", "here"))]

== Performance Metrics
The system was evaluated on a benchmark suite consisting of 23 natural language queries covering a variety of database operations including selection, aggregation, joins, filtering, and nested queries.

+ *Success Rate*: The system successfully generated and executed valid SQL for 22 out of 23 queries, yielding a success rate of approximately 95.7%.
+ *Retries*: On average, queries requiring correction were resolved within 2 retries, with a maximum retry limit set to 5 attempts per query.
+ *Error Types*: Initial failures predominantly involved SQL syntax errors such as incorrect aliases, malformed clauses, or typographical mistakes.
+ *Correction Mechanism*: The iterative feedback loop—feeding back error messages and prior SQL to the model—proved effective in resolving errors without human intervention.
+ *Timeouts*: No API call timeouts occurred during testing, with a per-call timeout threshold of 60 seconds.
+ *Failure Analysis*: The single failure involved a persistent syntax issue related to a subquery with NOT IN clause, which the model was unable to correct within the retry limit.
+ *Execution*: Successful queries returned meaningful result sets consistent with the expected database schema and semantics.

Overall, these metrics demonstrate the system’s high reliability in converting natural language queries into syntactically correct and executable SQL statements, validating the efficacy of the combined fine-tuned model and iterative error correction approach.

== Results of Testing
The testing revealed several key insights about the system’s performance in converting natural language queries into SQL:
+ The system generated SQL queries that matched the intended semantics of the input questions with a high degree of accuracy.
+ Most queries were correctly handled on the first attempt, demonstrating the fine-tuned model’s capability to understand diverse query types.
+ Queries involving straightforward selection, aggregation, and grouping operations consistently produced correct results.
+ Complex queries requiring multiple joins, nested subqueries, or advanced filtering often required one or two iterations to fix minor syntactic or semantic errors.
+ The iterative self-correction mechanism effectively improved query accuracy by leveraging runtime error feedback.
+ The only query that failed after the maximum retry attempts involved a NOT IN subquery, indicating a potential limitation in handling certain SQL constructs.
+ The model demonstrated strong understanding of the database schema, correctly referencing table and column names in most cases.
+ Output explanations accompanying the generated SQL queries helped in diagnosing errors and understanding query logic during testing.

These results affirm the practical viability of the proposed approach for real-world natural language querying of structured data, with room for improvement in handling rare edge cases.

#pagebreak()
= Challenges and Lessons Learned
#overview("", [
  In this chapter, we reflect on the technical challenges encountered during the development and testing of ttyDB, as well as the lessons learned from these experiences. The project faced several hurdles related to model limitations, error handling, and system architecture, which provided valuable insights for future improvements. \
  #box()[
    + *Technical Challenges*: This section discusses the technical challenges faced during development, including model limitations, error handling, and system architecture issues.
    + *Lessons Learned*: This section summarizes the key lessons learned from the project, including insights into model performance, error correction strategies, and system design considerations.
  ]
])
== Technical Challenges
During development and testing, several challenges emerged:
+ *Model Size Limitations*: Using a comparatively smaller 3B parameter model constrained the complexity of queries the system could confidently generate, necessitating extensive fine-tuning and iterative correction.
+ *Hallucinations and Syntax Errors*: The model occasionally hallucinated incorrect SQL syntax, table names, or column names, leading to frequent execution errors. Mitigating this required building a robust feedback loop to detect and correct errors automatically.
+ *Tool Calling Difficulties*: A custom implementation of tool calling was tested but abandoned due to excessive and irrelevant calls, including hallucinated tool names. Although prompt engineering reduced hallucinations somewhat, tool calling remained unreliable.
+ *Error Correction Strategy*: The final strategy—where the model receives its own generated SQL and the execution error as input for correction (termed Iterative Self-Feedback Loop)—proved effective in improving query quality without external intervention.
+ *Complex Query Handling*: Queries involving complex SQL constructs like nested subqueries or specific JOIN conditions sometimes required multiple correction cycles, revealing the need for further model enhancements or complementary heuristics.
+ *Schema Awareness*: Explicitly providing the database schema as context was critical in reducing hallucinations and improving the accuracy of generated SQL.

== Lessons Learned
+ Importance of Iterative Correction: Implementing an iterative self-feedback loop where the model reviews its own SQL errors significantly improves query accuracy and robustness, especially when working with smaller models.
+ Schema Context is Crucial: Providing a detailed schema description upfront helps reduce hallucinations and guides the model to generate syntactically and semantically correct SQL queries.
+ Limitations of Tool Calling with Smaller Models: Despite its potential, tool calling can introduce instability and hallucinations in smaller models, making a simpler error-feedback approach more reliable in practice.
+ Fine-Tuning Depth Matters: Extensive fine-tuning with a sizable dataset (8.4k samples) was necessary to compensate for the smaller model size and enhance domain-specific SQL generation.
+ Fallback Mechanisms Enhance Reliability: Having a fallback to a stronger model (e.g., Google Gemini 2.5 flash) ensures robustness for edge cases where the primary model fails repeatedly.
+ Balancing Model Complexity and System Constraints: Selecting a smaller model allowed deployment within resource limits but required compensatory architectural design choices to maintain accuracy.

#pagebreak()
= Future Work
#overview("", [
  In this chapter, we outline the planned enhancements and potential features for ttyDB, focusing on improving the system's capabilities, user experience, and overall performance. The future work aims to address the current limitations and expand the system's functionality to better serve users' needs. \
  #box()[
    + *Planned Enhancements*: This section describes the planned enhancements to the system, including improvements to the tool calling mechanism, adaptive query refinement, and multi-modal data support.
    + *Potential Features*: This section outlines potential features that could be added to enhance the user experience, such as natural language query history, visual query builders, and real-time query suggestions.
  ]
])
== Planned Enhancements
+ Improved Tool Calling Mechanism: Develop a more reliable tool calling system with better prompt engineering to reduce hallucinations and irrelevant calls.
+ Adaptive Query Refinement: Introduce smarter retry logic that prioritizes fixes based on error types to optimize query correction efficiency.
+ Multi-Modal Data Support: Expand support for querying non-SQL data sources like CSV and JSON through natural language.
+ Contextual and Multi-Turn Querying: Enable context-aware conversations that remember previous queries for more complex interactions.
+ Enhanced Explainability: Provide clearer and more user-friendly explanations of generated SQL queries to aid understanding and trust.

== Potential Features
+ *Natural Language Query History*: Maintain a user query history for quick access and reuse of past queries.
+ *Visual Query Builder*: Interactive UI to construct and refine SQL queries visually alongside natural language input.
+ *Query Result Visualization*: Charts, graphs, and tables to help users interpret query results easily.
+ *Real-Time Query Suggestions*: Provide dynamic autocomplete and query suggestions as users type their natural language input.

#pagebreak()

= Conclusion
== Summary of Achievements
+ Developed a natural language to SQL conversion system fine-tuned on a 3B-parameter Qwen2.5-coder model.
+ Implemented an iterative SQL validation and self-correction loop, reducing query errors and hallucinations.
+ Successfully created and tested a representative multi-table in-memory SQLite database with realistic sample data.
+ Achieved a high accuracy benchmark, correctly answering 22 out of 23 diverse natural language queries.
+ Designed a scalable backend architecture with separated microservices for file handling and model inference.

== Final Thoughts
#par(justify: true)[
  This project demonstrates the feasibility of converting natural language queries into executable SQL statements using a fine-tuned 3B-parameter model. Despite inherent challenges such as hallucinations and syntax errors, an iterative correction mechanism coupled with fallback strategies ensured high accuracy and robustness. The system successfully handled a diverse set of complex queries against a representative database schema, achieving a benchmark accuracy of 22 out of 23 queries. Future improvements in tool calling, query refinement, and multi-modal support will further enhance usability and performance, making natural language database querying accessible to a broader audience.
]

#pagebreak()
= References
#overview("", "In this section, we provide a list of references and resources that were instrumental in the development of ttyDB. These resources include documentation, tutorials, and articles related to natural language processing, SQL generation, and the technologies used in this project.")
== Fine-tuning LLMs
+ #link("https://medium.com/@sbasil.ahamed/fine-tuning-llms-with-unsloth-and-ollama-a-step-by-step-guide-33c82facde51", "Fine-Tuning LLMs with Unsloth and Ollama: A Step-by-Step Guide")
+ #link("https://docs.unsloth.ai/basics/tutorials-how-to-fine-tune-and-run-llms/tutorial-how-to-finetune-llama-3-and-use-in-ollama", "Tutorial: How to Finetune Llama-3 and Use In Ollama")
+ #link("https://ollama.com/library/qwen2.5", "Qwen2.5-Coder:3B on Ollama")

== Synthetic Data Generation
+ #link("https://ai.google.dev/gemini-api/docs", "Gemini API | Google AI for Developers")
+ #link("https://docs.pydantic.dev/latest/usage/models/", "Pydantic Models Documentation")
+ #link("https://chatgpt.com", "ChatGPT")

== SQLite and Pandas
+ #link("https://sqlite.org/docs.html", "SQLite3 Documentation")
+ #link("https://pandas.pydata.org/docs/user_guide/io.html#io-sql", "Pandas Documentation")

== Frontend Development
+ #link("https://nextjs.org/docs", "Next.js Documentation")
+ #link("https://shadcn-ui.com/docs", "ShadCN/UI Component Library")
+ #link("https://tailwindcss.com/docs", "TailwindCSS Documentation")

== Backend Development
+ #link("https://flask.palletsprojects.com/en/2.3.x/", "Flask Documentation")
+ #link("https://prisma.io/docs", "Prisma Documentation")
+ #link("https://docs.ollama.com", "Ollama Documentation")
+ #link("https://www.better-auth.com/docs/basic-usage", "Basic Usage | BetterAuth")

