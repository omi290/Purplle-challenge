# 📊 Validation Guide — Core Analytics and Math Engines

This document explains the mathematical formulas, database queries, and logical validations behind the retail intelligence engines in **Apex Retail Intelligence OS**.

---

## 1. Computer Vision Normalization Validation

Camera coordinates must map accurately to layout boundaries regardless of video resolution. We normalize all bounding box coordinates:

```python
# Bounding box center coordinates
cx = bbox_x + (bbox_w / 2.0)
cy = bbox_y + (bbox_h / 2.0)
```

Where `bbox_x`, `bbox_y`, `bbox_w`, and `bbox_h` are normalized percentages (between `0.0` and `1.0`) relative to the frame width and height.

---

## 2. Staff Exclude Engine Validation

Store associates are excluded from customer analytics using a color-based HSV mask with track-level majority voting.

### HSV Color Range:
* **Lower limit:** `[100, 50, 50]` (Purple/Pink Hue boundary)
* **Upper limit:** `[130, 255, 255]`

### Trajectory Voting Formula:
$$\text{Is Staff} = \frac{\sum_{t=1}^{T} \text{Frame Uniform Pixel Match}_t}{T} > 0.5$$

To verify employee filtering, run this query in your database:
```sql
SELECT track_id, is_staff, staff_confidence FROM visitors WHERE is_staff = TRUE;
```

---

## 3. Revenue Leakage Metric Validation

Revenue Leakage measures checkouts abandoned due to line delays:

$$\text{Revenue Leakage} = \text{Queue Abandonments} \times \text{Average Order Value (AOV)}$$

### Database Queries:
1. **Lost Customers:**
   ```sql
   SELECT COUNT(id) FROM events WHERE event_type = 'BILLING_QUEUE_ABANDON';
   ```
2. **Average Order Value (AOV):**
   ```sql
   SELECT AVG(total_amount) FROM transactions;
   ```

---

## 4. Opportunity Loss Metric Validation

Opportunity Loss represents missed revenue from unconverted traffic:

$$\text{Estimated Opportunity Loss} = \text{Unconverted Visitors} \times 0.15 \times \text{AOV}$$

Where **Unconverted Visitors** are computed as:
$$\text{Unconverted Visitors} = \text{Unique Customers} - \text{POS Transactions}$$

---

## 5. Stateful Queue Severity & Temporal Escalation

Evaluates wait times and escalates warnings statefully:
* **WARN:** Queue size exceeds 8 shoppers.
* **CRITICAL:** Queue remains bottlenecked ($\ge 8$ shoppers) for **$\ge 10$ minutes** consecutively.

To inspect queue alerts, run this query:
```sql
SELECT id, anomaly_type, severity, detected_at, resolved FROM anomalies WHERE anomaly_type = 'queue_spike';
```
