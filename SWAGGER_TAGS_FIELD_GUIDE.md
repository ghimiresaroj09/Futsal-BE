# How to Use the Tags Field in Swagger UI

## ⚠️ Common Error

If you see this error:
```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "tags": ["Value must be valid JSON."]
  }
}
```

It means you're not formatting the tags field correctly.

---

## ✅ Correct Way

When using the Swagger UI to test `/api/v1/cms/gallery/highlights/`, the `tags` field must be entered as a **JSON array string**.

### In the Swagger Form:

**Field**: `tags`  
**Type**: Array of tag strings

**❌ WRONG - Don't type:**
```
Saved
goal
goal, highlight
```

**✅ CORRECT - Type this:**
```
["goal", "highlight", "tournament"]
```

---

## Examples

### Example 1: Single Tag
```
["goal"]
```

### Example 2: Multiple Tags
```
["goal", "save", "skills"]
```

### Example 3: Empty Tags (Optional)
```
[]
```

Or just leave the field empty.

### Example 4: Tags with Spaces
```
["best goals", "championship 2026", "highlights"]
```

---

## Why This Format?

The `tags` field in the database is a `JSONField` that stores an array. When you use **multipart/form-data** (which Swagger uses for file uploads), the array needs to be sent as a JSON-formatted string.

### Behind the Scenes:

1. **Your Input**: `["goal", "highlight"]`
2. **Sent as**: String containing `["goal", "highlight"]`
3. **Serializer**: Parses the JSON string into a Python list
4. **Database**: Stores as JSON array

---

## Complete Example in Swagger

When creating a new highlight:

1. **title**: `Amazing Goals`
2. **video**: [Upload your video file]
3. **thumbnail**: [Upload thumbnail image] (optional)
4. **tags**: `["goal", "amazing", "2026"]` ← Use this format!
5. **is_active**: `true`
6. **sort_order**: `0`

Click "Execute" → Success! ✅

---

## Using cURL (Alternative)

If you prefer command line:

```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/highlights/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Amazing Goals" \
  -F "video=@video.mp4" \
  -F 'tags=["goal", "amazing", "2026"]' \
  -F "is_active=true"
```

Notice the single quotes around the tags value to preserve the double quotes inside.

---

## Using JSON (Alternative)

When using `Content-Type: application/json` (for PATCH updates without files):

```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/highlights/{id}/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["goal", "updated"]
  }'
```

In JSON format, tags is directly an array (no quotes around it).

---

## Quick Reference

| Scenario | Format | Example |
|----------|--------|---------|
| Swagger UI (multipart) | JSON string | `["goal", "save"]` |
| cURL (multipart -F) | JSON string in quotes | `-F 'tags=["goal"]'` |
| JSON request | Direct array | `{"tags": ["goal"]}` |
| Python/JavaScript | Array/List | `['goal', 'save']` |

---

## Validation Rules

✅ **Valid:**
- `["goal"]`
- `["goal", "save", "skills"]`
- `[]` (empty array)
- Leave field empty (becomes empty array)

❌ **Invalid:**
- `goal` (not an array)
- `"goal"` (string, not array)
- `["goal", ""]` (empty string in array)
- `Saved` (literal text)
- `[goal]` (missing quotes)

---

## Still Having Issues?

1. **Check the format**: Make sure you're using `["tag1", "tag2"]`
2. **Use double quotes**: Inside the array, use `"` not `'`
3. **Include the brackets**: `[` and `]` are required
4. **Separate with commas**: `["tag1", "tag2"]` not `["tag1" "tag2"]`

---

**Remember**: The word "Saved" you might see in Swagger is just a placeholder/label from the UI, not the value you should enter!

**Status**: ✅ Complete Guide
**Date**: September 10, 2026
