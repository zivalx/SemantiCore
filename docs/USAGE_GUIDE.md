# Complete Usage Guide

Comprehensive guide with detailed examples for every feature of Semantic Mapper.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Uploading Data](#uploading-data)
3. [Defining Your Domain](#defining-your-domain)
4. [Reviewing Ontology Proposals](#reviewing-ontology-proposals)
5. [Providing Feedback](#providing-feedback)
6. [Materializing the Graph](#materializing-the-graph)
7. [Querying Your Data](#querying-your-data)
8. [Common Workflows](#common-workflows)
9. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### Launch Options

**Option 1: Quick Start (Recommended)**
```bash
# Unix/Mac/Linux
./scripts/start.sh

# Windows
scripts\start.bat
```

**Option 2: Docker**
```bash
docker-compose up -d
```

**Option 3: Manual**
```bash
streamlit run src/semantic_mapper/ui/app.py
```

### First Time Setup

1. Open http://localhost:8501
2. You'll see the main dashboard
3. Check sidebar for status (should show Neo4j connection)
4. If Neo4j isn't connected, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Uploading Data

### Supported Formats

- **CSV** — Tabular data
- **JSON** — Structured data (objects or arrays)
- **Text/Markdown** — Unstructured text
- **PDF** — Documents
- **DOCX** — Word documents

### Example 1: CSV File (E-commerce Orders)

**File: `orders.csv`**
```csv
order_id,customer_name,product,quantity,price,date
1001,John Smith,Laptop,1,999.99,2024-01-15
1002,Jane Doe,Mouse,2,25.50,2024-01-16
```

**Steps:**
1. Click **Upload Data** in navigation
2. Click **Choose a file**
3. Select `orders.csv`
4. Settings:
   - **Delimiter**: `,` (comma)
   - **Encoding**: `utf-8`
5. Click **Ingest Data**

**Result:**
```
✅ Successfully ingested 2 records!

Sample Records:
Record 1:
{
  "order_id": "1001",
  "customer_name": "John Smith",
  "product": "Laptop",
  "quantity": "1",
  "price": "999.99",
  "date": "2024-01-15"
}
```

### Example 2: JSON File (Research Papers)

**File: `papers.json`**
```json
[
  {
    "title": "Deep Learning for NLP",
    "authors": ["Dr. Smith", "Prof. Johnson"],
    "year": 2023,
    "citations": 45
  }
]
```

**Steps:**
1. Upload `papers.json`
2. No special settings needed
3. Click **Ingest Data**

**Result:**
- Records with nested data flattened
- Author arrays converted to JSON strings
- All fields preserved

### Example 3: Text File (Documentation)

**File: `notes.txt`**
```
Project Requirements
===================

The system needs to handle customer data...

Implementation Notes
===================

We will use Python and Neo4j...
```

**Steps:**
1. Upload `notes.txt`
2. Settings:
   - **Split by**: `paragraph` (splits on blank lines)
3. Click **Ingest Data**

**Result:**
- 2 records (one per paragraph)
- Each paragraph becomes a separate record

### Example 4: PDF File

**File: `report.pdf`**

**Steps:**
1. Upload `report.pdf`
2. Settings:
   - **Extract by**: `page` (one record per page)
3. Click **Ingest Data**

**Result:**
- One record per page
- Text extracted from PDF
- Page numbers preserved

### Tips for Data Upload

✅ **Do:**
- Upload clean, representative data
- Use 10-100 records for initial testing
- Mix different data sources if needed
- Check sample records after upload

❌ **Don't:**
- Upload extremely large files (>100MB) initially
- Upload sensitive/private data without review
- Forget to check ingestion warnings

---

## Defining Your Domain

### What is a Domain Description?

A domain description is a plain-English explanation of:
- **What** your data represents
- **Who** the main actors/entities are
- **How** they relate to each other

### Example 1: E-commerce System

**Data:** Customer orders, products, shipping info

**Good Domain Description:**
```
This is an e-commerce order management system.

Customers place orders for products. Each order contains multiple
line items with specific quantities and prices. Orders are shipped
to addresses and have statuses (pending, shipped, delivered).

Products have names, prices, and belong to categories. We track
inventory levels and supplier information.

Customers have email addresses, shipping preferences, and order
history. Some customers are premium members with special pricing.
```

**Why it's good:**
- ✅ Explains main entities (Customer, Order, Product)
- ✅ Describes relationships (Customer→Order, Order→Product)
- ✅ Mentions important attributes (status, quantity, price)
- ✅ Includes business rules (premium members, inventory tracking)

**Bad Domain Description:**
```
This is order data from our database.
```

**Why it's bad:**
- ❌ Too vague
- ❌ Doesn't explain semantics
- ❌ No relationship information

### Example 2: Research Papers

**Data:** Academic papers with authors, citations

**Good Domain Description:**
```
This is a research paper citation network.

Papers are written by one or more Authors. Authors can collaborate
on multiple papers. Papers cite other papers, forming a citation
network.

Each paper has a title, abstract, publication year, and venue
(conference or journal). Papers are tagged with keywords for
categorization.

Authors are affiliated with Institutions (universities, companies).
We track citation counts to measure impact.
```

### Example 3: Healthcare Records

**Data:** Patients, diagnoses, treatments

**Good Domain Description:**
```
This is a simplified patient health record system.

Patients have demographics (age, gender) and visit medical
Facilities for care. During visits, they receive Diagnoses
and Treatments from Healthcare Providers (doctors, nurses).

Diagnoses are coded using standard medical codes. Treatments
include medications, procedures, and therapies. We track
outcomes and follow-up appointments.

Patients can have multiple chronic conditions. Some treatments
require pre-authorization from insurance.
```

### Tips for Domain Descriptions

✅ **Do:**
- Use clear, simple language
- Mention all major entity types
- Describe key relationships
- Include business rules/constraints
- Provide 2-3 paragraphs of detail

❌ **Don't:**
- Use technical jargon unnecessarily
- Just list field names
- Leave out important context
- Make it too short (<50 words)

### Generating the Proposal

1. Write your domain description
2. (Optional) Adjust **Sample Size** (default: 10 records)
3. Click **Generate Proposal**
4. Wait 30-60 seconds
5. Review the generated ontology

---

## Reviewing Ontology Proposals

### What You'll See

The LLM generates a proposal with:

1. **Overall Explanation** — High-level modeling approach
2. **Classes** — Entity types (e.g., Customer, Order, Product)
3. **Relationships** — How classes connect
4. **Confidence Scores** — How certain the LLM is
5. **Open Questions** — What the LLM is unsure about
6. **Alternatives** — Different ways to model things

### Example Proposal Review

**Proposal for E-commerce System:**

#### Classes

**1. Customer**
- **Label:** Customer
- **Description:** A person or organization that places orders
- **Rationale:** Clear entity representing buyers
- **Confidence:** 95%
- **Properties:**
  - `customer_name` (string, required)
  - `customer_email` (string, required)
- **Open Questions:**
  - Should we distinguish between individual and business customers?

**2. Order**
- **Label:** Order
- **Description:** A purchase request placed by a customer
- **Confidence:** 90%
- **Properties:**
  - `order_id` (string, required, unique)
  - `order_date` (date, required)
  - `status` (string)
- **Rationale:** Central entity connecting customers and products

**3. Product**
- **Label:** Product
- **Description:** An item available for purchase
- **Confidence:** 85%
- **Properties:**
  - `product_name` (string, required)
  - `price` (float, required)

#### Relationships

**1. PLACED_BY**
- **Source:** Order
- **Target:** Customer
- **Cardinality:** many-to-one (many orders per customer)
- **Description:** Links orders to the customer who placed them
- **Confidence:** 95%

**2. CONTAINS**
- **Source:** Order
- **Target:** Product
- **Cardinality:** many-to-many (orders can have multiple products)
- **Description:** Products included in an order
- **Confidence:** 80%
- **Open Questions:**
  - Should we model OrderLineItem as a separate entity to capture quantity and per-item price?

### How to Review

#### Check Classes

For each class, ask yourself:
- ✅ Does the name make sense?
- ✅ Is the description accurate?
- ✅ Are properties correct?
- ✅ Should this be split into multiple classes?
- ✅ Should this be merged with another class?

#### Check Relationships

For each relationship, ask:
- ✅ Does the direction make sense?
- ✅ Is the cardinality correct?
- ✅ Should there be additional relationships?

#### Common Issues to Fix

**Issue 1: Missing Entity**
```
❌ Missing: Address class
✅ Fix: Request "Add Address class for shipping/billing"
```

**Issue 2: Wrong Cardinality**
```
❌ Customer→Order is one-to-one
✅ Fix: Should be one-to-many (customers have multiple orders)
```

**Issue 3: Missing Intermediate Entity**
```
❌ Order→Product (many-to-many) doesn't capture quantity
✅ Fix: Add OrderLineItem entity to store quantity and price
```

---

## Providing Feedback

### Option 1: Accept the Proposal

If the ontology looks good:
1. Click **✅ Accept Ontology**
2. System saves to Neo4j
3. Proceed to materialization

### Option 2: Request Modifications

If you want changes:

**Example Feedback:**
```
Please make these changes:

1. Rename "Customer" to "Buyer" to match our business terminology

2. Split "Product" into two classes:
   - "Product" (template/catalog item)
   - "ProductVariant" (specific SKU with size/color)

3. Add "OrderLineItem" entity between Order and Product to capture:
   - quantity
   - unit_price
   - line_total

4. Add "Address" class with properties:
   - street
   - city
   - state
   - postal_code

5. Add relationship: Order→SHIPS_TO→Address

6. Change Order→Product cardinality from many-to-many to:
   Order→CONTAINS→OrderLineItem→FOR_PRODUCT→Product
```

**Steps:**
1. Click **✏️ Request Modifications**
2. Enter your feedback
3. Click **Submit Feedback**
4. Go back to **Define Domain**
5. Click **Generate Proposal** again (iteration 2)

### Option 3: Request New Proposal

If you want to start over:
1. Click **🔄 Request New Proposal**
2. Update domain description
3. Generate again

### Feedback Best Practices

✅ **Do:**
- Be specific (cite class/relationship names)
- Explain WHY you want changes
- Provide examples if helpful
- Number your feedback points

❌ **Don't:**
- Just say "fix it"
- Provide conflicting instructions
- Change too many things at once

---

## Materializing the Graph

### Current State: Manual Creation

**Note:** Automatic materialization requires LLM-based record mapping. For transparency, we keep this manual initially.

### Creating Instance Nodes

**Example: Create a Customer**

1. Go to **Materialize Graph**
2. Select class: **Customer**
3. Fill properties:
   - `customer_name`: "John Smith"
   - `customer_email`: "john@example.com"
4. Click **Create Instance**

**Result:**
```
✅ Created instance: 4:a1b2c3d4:0
```

### Creating Multiple Instances

Repeat for each entity type:

**Customer instances:**
- John Smith, john@example.com
- Jane Doe, jane@example.com

**Product instances:**
- Laptop, $999.99
- Mouse, $25.50

**Order instances:**
- Order #1001, 2024-01-15, shipped
- Order #1002, 2024-01-16, delivered

### Future: Automatic Materialization

In production, you would:
1. Upload data
2. LLM maps records to classes
3. LLM extracts relationships
4. System creates all instances automatically
5. Human reviews and corrects

---

## Querying Your Data

### Natural Language Queries

**Example 1: Count Entities**

**Question:**
```
How many customers are there?
```

**Translation Result:**
- **Cypher:**
  ```cypher
  MATCH (c:Instance)-[:INSTANCE_OF]->(class:OntologyClass {name: 'Customer'})
  RETURN count(c) as customer_count
  ```
- **Explanation:** This query finds all instances that are linked to the Customer class and counts them.
- **Confidence:** 95%

**Execute → Results:**
```
customer_count: 2
```

**Example 2: Find Relationships**

**Question:**
```
Show me all orders and their customers
```

**Translation Result:**
- **Cypher:**
  ```cypher
  MATCH (o:Instance)-[:INSTANCE_OF]->(o_class:OntologyClass {name: 'Order'})
  MATCH (o)-[r:RELATED {type: 'PLACED_BY'}]->(c:Instance)
  MATCH (c)-[:INSTANCE_OF]->(c_class:OntologyClass {name: 'Customer'})
  RETURN o.order_id as order, c.customer_name as customer
  ```
- **Explanation:** Finds orders, follows PLACED_BY relationship to customers, returns both.

**Example 3: Aggregation**

**Question:**
```
How many orders did each customer place?
```

**Translation Result:**
- **Cypher:**
  ```cypher
  MATCH (c:Instance)-[:INSTANCE_OF]->(:OntologyClass {name: 'Customer'})
  MATCH (o:Instance)-[:INSTANCE_OF]->(:OntologyClass {name: 'Order'})
  WHERE (o)-[:RELATED {type: 'PLACED_BY'}]->(c)
  RETURN c.customer_name as customer, count(o) as order_count
  ORDER BY order_count DESC
  ```

### Direct Cypher Queries

If you know Cypher, you can write queries directly:

**Example: Get All Instances**
```cypher
MATCH (i:Instance)
RETURN i
LIMIT 10
```

**Example: View Ontology Structure**
```cypher
MATCH (o:Ontology)-[:DEFINES]->(c:OntologyClass)
RETURN o.name as ontology, collect(c.name) as classes
```

**Example: Find Relationships Between Instances**
```cypher
MATCH (s:Instance)-[r:RELATED]->(t:Instance)
RETURN s, r, t
LIMIT 10
```

### Query Tips

✅ **Do:**
- Start with simple queries
- Review generated Cypher before executing
- Use LIMIT for large result sets
- Save successful queries for reuse

❌ **Don't:**
- Write destructive queries (DELETE, DETACH DELETE)
- Query without LIMIT on large graphs
- Expect perfect translations (always review)

---

## Common Workflows

### Workflow 1: New Project from Scratch

```
1. Start application
2. Upload example data (10-50 records)
3. Write domain description
4. Generate ontology proposal
5. Review and accept
6. Create sample instances manually
7. Test with queries
8. Upload full dataset
9. Implement auto-materialization
```

### Workflow 2: Refining an Existing Ontology

```
1. Review current ontology in Neo4j
2. Identify issues (missing classes, wrong relationships)
3. Write detailed feedback
4. Generate new proposal (iteration N+1)
5. Compare with previous version
6. Accept improvements
7. Migrate existing instances if needed
```

### Workflow 3: Exploring New Dataset

```
1. Upload unknown dataset
2. Let system analyze patterns
3. Read LLM's interpretation
4. Provide domain expertise
5. Iterate until ontology matches reality
6. Document decisions for future reference
```

### Workflow 4: Querying Existing Graph

```
1. Understand ontology structure
2. Ask questions in natural language
3. Review generated Cypher
4. Learn Cypher patterns
5. Write custom queries
6. Export results
```

---

## Tips & Best Practices

### Data Preparation

✅ Clean data before upload
✅ Remove duplicates
✅ Fix obvious errors
✅ Use consistent naming
✅ Include representative samples

### Domain Descriptions

✅ Be detailed (2-3 paragraphs)
✅ Use business terminology
✅ Mention relationships explicitly
✅ Include constraints/rules
✅ Give examples

### Ontology Review

✅ Check all class names
✅ Verify all relationships
✅ Review cardinalities
✅ Look for missing entities
✅ Consider future needs

### Feedback

✅ Be specific
✅ Explain reasoning
✅ One change at a time
✅ Test incrementally
✅ Document decisions

### Querying

✅ Start simple
✅ Use LIMIT
✅ Review Cypher
✅ Save good queries
✅ Learn patterns

### Performance

✅ Index frequently queried properties
✅ Use WHERE clauses
✅ Limit result sizes
✅ Profile slow queries
✅ Batch large operations

---

## Troubleshooting Common Issues

### Issue: Proposal Doesn't Match Expectations

**Solution:**
- Provide more detailed domain description
- Give specific examples in description
- Explicitly mention missing entities
- Request modifications with clear guidance

### Issue: Query Returns No Results

**Solutions:**
1. Check if instances exist: `MATCH (i:Instance) RETURN count(i)`
2. Verify relationships: `MATCH ()-[r:RELATED]->() RETURN count(r)`
3. Check class names: `MATCH (c:OntologyClass) RETURN c.name`
4. Review query Cypher for errors

### Issue: Too Many Classes Generated

**Solution:**
- Simplify domain description
- Request merging of similar classes
- Focus on core entities first
- Iterate to simplify

### Issue: LLM Unsure About Modeling

**Solution:**
- LLM's uncertainty means YOU need to decide
- Review "Open Questions" section
- Provide explicit guidance in feedback
- Trust your domain expertise

---

## Next Steps

After mastering basic usage:

1. ✅ Implement automatic materialization
2. ✅ Add relationship extraction
3. ✅ Build custom visualizations
4. ✅ Create saved query templates
5. ✅ Set up automated pipelines
6. ✅ Integrate with other tools

---

**Need more help?** See [QUICK_START.md](QUICK_START.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
