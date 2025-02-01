This PR implements proper handling of deleted documents in MongoDB Change Data Capture (CDC). Previously, the system only handled insert and update operations while skipping delete operations. The implementation now properly captures and processes delete operations in the CDC stream, including metadata such as deletion timestamp and namespace information.

PR :https://github.com/datazip-inc/olake/pull/80

1. First, let's understand what CDC (Change Data Capture) is:
   - CDC tracks changes in a database (like inserts, updates, and deletes)
   - It's like keeping a log of everything that happens to your data

2. The Original Problem:
   - The code was only handling when records were added (insert) or modified (update)
   - It wasn't handling when records were deleted
   - This meant that deletions in MongoDB weren't being tracked

3. Key Structure Changes:
```go
// Old version
type CDCDocument struct {
    OperationType string         `json:"operationType"`
    FullDocument  map[string]any `json:"fullDocument"`
}

// New version
type CDCDocument struct {
    OperationType string         `json:"operationType"`
    FullDocument  map[string]any `json:"fullDocument"`
    DocumentKey   map[string]any `json:"documentKey"`   // Added this
    NS            struct {                              // Added this
        DB         string `json:"db"`
        Collection string `json:"coll"`
    } `json:"ns"`
}
```
Explanation:
- `OperationType`: Tells us what happened (insert/update/delete)
- `FullDocument`: Contains the actual document data
- `DocumentKey`: Added to keep track of which document was deleted
- `NS`: Added to store database and collection names

4. The Main Processing Changes:
```go
// Old code
if record.FullDocument != nil {
    record.FullDocument["cdc_type"] = record.OperationType
}

// New code
var documentToProcess map[string]any
switch record.OperationType {
case "delete":
    documentToProcess = map[string]any{
        "_id":            record.DocumentKey["_id"],
        "cdc_type":       record.OperationType,
        "deleted_at":     time.Now().UTC().Format(time.RFC3339),
        "document_key":   record.DocumentKey,
        "namespace_db":   record.NS.DB,
        "namespace_coll": record.NS.Collection,
    }
default:
    if record.FullDocument != nil {
        documentToProcess = record.FullDocument
        documentToProcess["cdc_type"] = record.OperationType
    }
}
```
Explanation:
- When a delete happens:
  - We create a new document to record the deletion
  - We store:
    - The ID of the deleted document
    - The fact that it was a deletion (`cdc_type`)
    - When it was deleted (`deleted_at`)
    - Where it was deleted from (database and collection names)
- For inserts and updates:
  - We keep the existing behavior
  - Just mark what type of operation it was

5. Important Go Concepts Used:
- `struct`: Like a template for data (similar to classes in other languages)
- `map[string]any`: A dictionary/hash map that can store any type of value
- `switch`: Like an if-else statement but cleaner for multiple conditions
- Time handling: `time.Now().UTC()` gets current time in UTC format

6. The Flow of Operations:
```
For Inserts/Updates:
MongoDB Change → Get Full Document → Add Operation Type → Save

For Deletes:
MongoDB Change → Get Document Key → Create Deletion Record → Add Metadata → Save
```

7. Key Benefits of These Changes:
- You now know when a document was deleted
- You know which document was deleted (via DocumentKey)
- You know where it was deleted from (database and collection)
- Existing insert/update functionality remains unchanged

Example of what happens when a document is deleted:
```json
// When you delete a document like this in MongoDB:
db.users.deleteOne({ "_id": "123" })

// The system now creates a record like this:
{
    "_id": "123",
    "cdc_type": "delete",
    "deleted_at": "2025-02-01T12:47:25Z",
    "document_key": { "_id": "123" },
    "namespace_db": "mydb",
    "namespace_coll": "users"
}
```

Would you like me to:
1. Explain any specific part in more detail?
2. Show more examples of how this works?
3. Explain any Go-specific concepts further?
