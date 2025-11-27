# Data Flow to Charts - Summary

## 📊 How Many Data Points Are Being Sent to Charts?

### **Answer: 20 data points per chart**

---

## 🔄 Complete Data Flow

### **1. Source Data (JSON File)**
- **File:** `backend/sensor_data_3params.json`
- **Total Records:** 10,000 sensor readings
- **Machines:** Machine_A, Machine_B, Machine_C
- **Parameters:** temperature, vibration, speed, timestamp

### **2. Backend Processing**
**Location:** `backend/app.py` - `/api/sensor-data` endpoint

**Step 1: Load & Group by Machine**
```python
# Groups all 10,000 records by machine_id
machine_map = make_machine_map_from_rows(raw_rows)
# Result: 
# - Machine_A: ~3,333 records
# - Machine_B: ~3,333 records  
# - Machine_C: ~3,334 records
```

**Step 2: Downsample (if needed)**
```python
def downsample_arrays(ts, arrays_dict, max_points=1000):
    # If data > 1000 points, downsample by averaging buckets
    # Otherwise, return all data
```

**Backend sends:** Up to 1,000 points per machine to frontend

### **3. Frontend Limiting**
**Location:** `frontend/src/pages/Dashboard.jsx` (line 68)

```javascript
const DPs = 20; // max datapoints
const limited = {
  timestamps: machineData.timestamps.slice(-DPs),
  temperature: machineData.temperature.slice(-DPs).map(Number),
  vibration: machineData.vibration.slice(-DPs).map(Number),
  speed: machineData.speed.slice(-DPs).map(Number),
};
```

**Frontend displays:** Last 20 data points only

### **4. Live Simulation**
**Location:** `frontend/src/pages/Dashboard.jsx` (line 88)

```javascript
const interval = setInterval(() => {
  // Every 5 seconds:
  // - Removes oldest point (index 0)
  // - Adds new simulated point
  // - Keeps array at exactly 20 points
}, 5000);
```

**Result:** Charts always show exactly 20 points, continuously updating

---

## 📈 Chart Data Breakdown

### **Line Chart (Temperature & Vibration)**
- **Data Points:** 20 timestamps
- **Temperature Array:** 20 values
- **Vibration Array:** 20 values
- **Updates:** Every 5 seconds (rolling window)

### **Bar Chart (Speed)**
- **Data Points:** 20 timestamps
- **Speed Array:** 20 values
- **Updates:** Every 5 seconds (rolling window)

### **Pie Chart (Load Distribution)**
- **Data Points:** 3 categories (High/Medium/Low)
- **Based on:** Latest speed value from the 20-point array
- **Updates:** Every 5 seconds

---

## 🎯 Why 20 Points?

**Advantages:**
1. ✅ **Clean Visualization** - Not too cluttered
2. ✅ **Real-time Feel** - Updates every 5 seconds
3. ✅ **Performance** - Fast rendering
4. ✅ **Trend Visibility** - Enough to see patterns
5. ✅ **LSTM Compatible** - Uses last 10 for predictions

**Trade-offs:**
- Shows only ~100 seconds of history (20 points × 5 sec)
- Historical data available but not displayed

---

## 🔢 Data Point Summary

| Stage | Data Points | Notes |
|-------|-------------|-------|
| **JSON File** | 10,000 total | All historical data |
| **Per Machine** | ~3,333 each | Grouped by machine_id |
| **Backend Sends** | Up to 1,000 | Downsampled if needed |
| **Frontend Receives** | Up to 1,000 | From API call |
| **Frontend Displays** | **20** | Last 20 points only |
| **Charts Show** | **20** | Rolling window |
| **LSTM Uses** | 10 | Last 10 for prediction |

---

## 💡 To Change Number of Points

### **Show More Points (e.g., 50)**
```javascript
// In Dashboard.jsx, line 68
const DPs = 50; // Change from 20 to 50
```

### **Show Less Points (e.g., 10)**
```javascript
// In Dashboard.jsx, line 68
const DPs = 10; // Change from 20 to 10
```

### **Show All Available Data**
```javascript
// In Dashboard.jsx, line 70-74
// Remove .slice(-DPs) to show all data
const limited = {
  timestamps: machineData.timestamps,
  temperature: machineData.temperature.map(Number),
  vibration: machineData.vibration.map(Number),
  speed: machineData.speed.map(Number),
};
```

---

## 🎬 Real-Time Updates

**Current Behavior:**
1. Initial load: Fetches last 20 points from backend
2. Every 5 seconds: Simulates new sensor reading
3. Removes oldest point, adds newest
4. Charts re-render with updated 20 points
5. Averages recalculated
6. Health summary updated

**Data Sent to ML Models:**
- **Random Forest:** Latest 1 point (3 features)
- **Isolation Forest:** Latest 1 point (3 features)
- **LSTM:** Last 10 points (sequence of 10 × 3)

---

## ✅ Summary

**Your charts are displaying 20 data points** from a pool of 10,000 historical records, with live simulation adding new points every 5 seconds in a rolling window fashion.
