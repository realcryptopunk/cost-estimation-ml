# BuildScan iOS App — Implementation Plan

## Overview

BuildScan is an iOS app for contractors that combines LiDAR room scanning, Claude AI-powered build list generation, and regional cost adjustment using the thesis CCI pipeline. The user scans a room (or takes a photo), describes the project, and gets an itemized material + labor estimate adjusted to their local market. Output is exportable as branded PDF.

**Thesis connection:** The BLS/FRED-based CCI pipeline provides the regional pricing engine, validated by the multi-model comparison and ablation study (+0.85% R² lift from CCI features).

---

## Architecture

```
[LiDAR Scan / Photo / Manual Entry]
         │
         ▼
[RoomMeasurementExtractor] → RoomData (sqft, walls, windows, doors)
         │
         ▼
[ClaudePromptBuilder] → structured prompt with measurements + project description
         │
         ▼
[Claude API (Sonnet)] → JSON build list (items, quantities, units, categories)
         │
         ▼
[CostEngine] → applies CCI regional adjustment + base pricing → PricedEstimate
         │
         ▼
[EstimateResultView] → itemized display → PDF export
```

**Key design rule:** Claude generates quantities and items. The CostEngine applies pricing. Never ask Claude for dollar amounts — it hallucinates prices. Pricing is deterministic from embedded CCI data.

---

## Data Files from ML Pipeline (copy into app bundle)

Export these from the constructionML repo:

| File | Source | Size | Purpose |
|------|--------|------|---------|
| `cci_table.json` | `data/raw/real_cci_table.csv` | ~57KB | Regional CCI lookup by state+year |
| `base_prices.json` | Curated | ~20KB | National average unit prices by category |
| `shap_importance.json` | `results/shap_importance_export.json` | ~7KB | Feature importance for explainability |
| `macro_snapshot.json` | `data/raw/fred_macro.csv` (latest year) | ~2KB | Current FRED values |

**Run `src/export_app_data.py` to generate these** (needs to be created in the ML repo).

CCI weighting formula (matches Python pipeline):
```
weighted_cci = 0.45 × mat_cci + 0.40 × labor_cci + 0.15 × equip_cci
```

---

## Xcode Project Structure

```
BuildScan/
├── App/
│   ├── BuildScanApp.swift              # @main entry, dependency injection
│   └── AppConfiguration.swift          # API key from Keychain, feature flags
├── Models/
│   ├── RoomData.swift                  # RoomData, WallSurface, Opening structs
│   ├── BuildList.swift                 # BuildListResponse, LineItem (Claude output)
│   ├── PricedEstimate.swift            # PricedLineItem, PricedEstimate
│   ├── ProjectType.swift               # 5 types with cost multipliers + icons
│   └── CCIData.swift                   # CCIEntry, regional lookup
├── Services/
│   ├── RoomPlan/
│   │   ├── RoomMeasurementExtractor.swift   # CapturedRoom → RoomData
│   │   └── RoomScanCoordinator.swift        # UIKit delegate bridge
│   ├── Claude/
│   │   ├── ClaudeAPIClient.swift            # HTTP + retry + error handling
│   │   ├── ClaudePromptBuilder.swift        # System + user prompt construction
│   │   └── BuildListParser.swift            # JSON parse with fallback layers
│   ├── Pricing/
│   │   ├── CostEngine.swift                 # CCI lookup + pricing
│   │   └── BasePriceDatabase.swift          # National avg unit prices
│   └── Export/
│       └── PDFExporter.swift                # Branded PDF generation
├── ViewModels/
│   └── EstimateViewModel.swift         # Orchestrates full pipeline
├── Views/
│   ├── Scan/
│   │   ├── ScanMethodPickerView.swift       # LiDAR vs photo vs manual
│   │   ├── RoomScanView.swift               # RoomCaptureView wrapper
│   │   ├── ManualRoomEntryView.swift        # Fallback: L/W/H entry
│   │   └── PhotoCaptureView.swift           # Camera for non-LiDAR
│   ├── Project/
│   │   ├── ProjectDescriptionView.swift     # Scope of work + type picker
│   │   └── LocationPickerView.swift         # State/region for CCI
│   ├── Results/
│   │   ├── EstimateResultView.swift         # Full estimate display
│   │   ├── LineItemListView.swift           # Items grouped by category
│   │   ├── Model3DPreviewView.swift         # USDZ QuickLook (wow factor)
│   │   └── EstimateSummaryCard.swift        # Totals: material/labor/overhead
│   └── Common/
│       ├── DesignTokens.swift               # Colors, fonts, spacing
│       └── LoadingStateView.swift           # Multi-phase progress
└── Resources/
    ├── cci_table.json
    ├── base_prices.json
    ├── shap_importance.json
    └── Assets.xcassets
```

---

## Core Data Models

### RoomData.swift
```swift
struct RoomData: Codable {
    let source: ScanSource              // .lidar, .photo, .manual
    let floorAreaSqft: Double
    let wallSurfaces: [WallSurface]
    let windows: [Opening]
    let doors: [Opening]
    let ceilingHeightFt: Double
    let furniture: [FurnitureItem]
    let usdzModelURL: URL?              // 3D export for client demos

    var totalWallAreaSqft: Double { wallSurfaces.reduce(0) { $0 + $1.areaSqft } }
    var netWallAreaSqft: Double {
        totalWallAreaSqft
        - windows.reduce(0) { $0 + $1.areaSqft }
        - doors.reduce(0) { $0 + $1.areaSqft }
    }
}

struct WallSurface: Codable {
    let widthFt: Double
    let heightFt: Double
    var areaSqft: Double { widthFt * heightFt }
}

struct Opening: Codable {
    let type: OpeningType   // .window, .door
    let widthFt: Double
    let heightFt: Double
    var areaSqft: Double { widthFt * heightFt }
}
```

### BuildList.swift (Claude's JSON output)
```swift
struct BuildListResponse: Codable {
    let projectSummary: String
    let lineItems: [LineItem]
    let assumptions: [String]
    let warnings: [String]
}

struct LineItem: Codable, Identifiable {
    let id = UUID()
    let item: String
    let quantity: Double
    let unit: String           // sqft, lf, ea, gal, sheets, hours, bags, boxes, rolls
    let category: String       // demolition, framing, drywall, electrical, plumbing, etc.
    let specification: String  // size, grade, model detail
    let confidence: String     // high, medium, low
}
```

### PricedEstimate.swift
```swift
struct PricedEstimate {
    let items: [PricedLineItem]
    let subtotal: Double
    let overhead: Double       // 10%
    let profit: Double         // 10%
    let contingency: Double    // 5%
    let cciApplied: CCIEntry
    let location: String

    var grandTotal: Double { subtotal + overhead + profit + contingency }
    var materialTotal: Double { items.reduce(0) { $0 + $1.materialCost } }
    var laborTotal: Double { items.reduce(0) { $0 + $1.laborCost } }
}

struct PricedLineItem {
    let lineItem: LineItem
    let materialCost: Double
    let laborCost: Double
    var totalCost: Double { materialCost + laborCost }
}
```

### ProjectType.swift
```swift
enum ProjectType: String, CaseIterable, Codable {
    case commercial = "Commercial"
    case residential = "Residential"
    case industrial = "Industrial"
    case institutional = "Institutional"
    case infrastructure = "Infrastructure"

    var costMultiplier: Double {
        switch self {
        case .commercial:     return 1.00
        case .residential:    return 0.85
        case .industrial:     return 0.90
        case .institutional:  return 1.15
        case .infrastructure: return 1.25
        }
    }

    var icon: String {
        switch self {
        case .commercial:     return "building.2"
        case .residential:    return "house"
        case .industrial:     return "gearshape.2"
        case .institutional:  return "building.columns"
        case .infrastructure: return "road.lanes"
        }
    }
}
```

---

## RoomPlan Integration

### RoomScanView — UIViewControllerRepresentable wrapping RoomCaptureView
- iOS 17+, requires LiDAR (iPhone 12 Pro+, iPad Pro)
- On completion: `CapturedRoom` with walls, doors, windows, floors, objects

### RoomMeasurementExtractor
- Converts `CapturedRoom` (meters, 3D) → `RoomData` (feet, 2D summary)
- RoomPlan dimensions: `.x` = width, `.y` = height, `.z` = depth. All in meters.
- Multiply by 3.28084 for feet.
- Also exports USDZ via `room.export(to: url)` for client-facing 3D preview.

### Fallback for non-LiDAR devices
- `ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh)` detects LiDAR
- Without LiDAR: photo capture + manual dimension entry (length, width, ceiling height, window/door count)
- Both paths produce the same `RoomData` struct — downstream pipeline is identical

### Navigation flow
```
ScanMethodPickerView
  ├── Has LiDAR → "Scan Room" → RoomScanView → auto-extract
  ├── Has LiDAR → "Enter Manually" → ManualRoomEntryView
  └── No LiDAR  → "Take Photo" → PhotoCaptureView + ManualRoomEntryView
All paths → ProjectDescriptionView → LocationPickerView → [Generate Estimate]
```

---

## Claude API Integration

### System Prompt
```
You are a construction estimating assistant for licensed contractors.
You generate material and labor build lists for construction projects.

RULES:
1. Return ONLY valid JSON. No markdown, no commentary, no code fences.
2. Use the exact schema below. Every field is required.
3. Quantities must be realistic for the given room dimensions.
4. Round quantities to standard purchase units (drywall in full sheets,
   lumber in 8/10/12 ft lengths, paint in gallons).
5. Include both material AND labor line items.
6. Labor items use unit="hours" and category="labor".
7. Include demolition/removal if scope implies it.
8. Apply waste factors: drywall 10%, tile 15%, paint 5%, lumber 10%, flooring 10%.
9. If uncertain, include with confidence="low".

RESPONSE SCHEMA:
{
  "project_summary": "string",
  "line_items": [
    {
      "item": "string — specific product/task",
      "quantity": number,
      "unit": "sqft|lf|ea|gal|sheets|hours|bags|boxes|rolls",
      "category": "demolition|framing|drywall|electrical|plumbing|hvac|flooring|paint|tile|insulation|fixtures|hardware|roofing|concrete|labor|permits|equipment_rental",
      "specification": "size, grade, or model detail",
      "confidence": "high|medium|low"
    }
  ],
  "assumptions": ["string"],
  "warnings": ["string"]
}
```

### User Prompt Construction (ClaudePromptBuilder)
Built from:
- Project type context (Commercial → ADA compliance, commercial-grade; Residential → IRC code; Industrial → OSHA, heavy-duty; Institutional → Davis-Bacon prevailing wage; Infrastructure → traffic control, bonding)
- Scope of work (user's text description)
- Room measurements (floor area, ceiling height, wall count, total wall area, net wall area, windows, doors, furniture detected)
- Individual wall dimensions

### Multi-modal (photo)
When photo is provided, send as base64 JPEG via Claude's vision capability. Claude uses visual details to refine quantities and material selections.

### Model: Claude Sonnet (fast enough for mobile UX, 3-8s response)

### Error handling
- 429 rate limit: exponential backoff, max 3 retries
- 529 overloaded: retry once after 10s
- Non-JSON response: 3-layer parser (strict decode → lenient clean → manual extraction)
- Empty line_items: retry with more specific prompt

---

## Cost Engine

### CostEngine.swift

1. Load `cci_table.json` — lookup by state + year
2. Load `base_prices.json` — national average unit prices by category
3. For each line item:
   - `materialCost = baseMaterial × (matCCI / 100) × quantity`
   - `laborCost = baseLabor × (laborCCI / 100) × quantity`
4. Apply `projectType.costMultiplier`
5. Add overhead (10%), profit (10%), contingency (5%)
6. Fallback: state not found → regional average. Region not found → national (all 100).

### CCI data comes from the thesis pipeline
- `labor_cci`: BLS OEWS construction wages by state, normalized to national=100
- `mat_cci`: FRED PPI for construction materials with regional labor adjustment
- `equip_cci`: FRED PPI durable goods (national, equipment is mobile)
- `weighted_cci`: 0.45×mat + 0.40×labor + 0.15×equip

---

## PDF Export

### PDFExporter.swift
- Header: contractor name/logo, date, project summary
- Body: line items grouped by category, each with qty, unit, material $, labor $, total $
- Summary: material subtotal, labor subtotal, overhead, profit, contingency, grand total
- Footer: "Regional adjustment: [state] CCI = [value]", "Powered by BuildScan"
- Optional: QR code linking to USDZ 3D model

---

## EstimateViewModel — Orchestration

```
@MainActor class EstimateViewModel: ObservableObject

States: idle → scanning → extractingMeasurements → generatingBuildList → applyingPricing → complete

processScan(room, description, type, location, photo):
  1. Extract RoomData from CapturedRoom (or manual/photo input)
  2. Export USDZ in parallel (if LiDAR scan)
  3. Build prompt from RoomData + description + type
  4. Call Claude API → parse BuildListResponse
  5. Apply CostEngine pricing with CCI for user's state
  6. Publish PricedEstimate → navigate to results
```

---

## Design Tokens

**Colors:** Accent blue #1A73E8, dark #0D47A1, light #E3F2FD. Cost-up red #D32F2F, cost-down green #2E7D32.

**Region palette:** Midwest #42A5F5, Northeast #1565C0, Southeast #66BB6A, Southwest #FFA726, West #AB47BC.

**Typography:** Hero 48pt rounded bold, section 18pt semibold, body 15pt, caption 12pt.

**Cards:** White background, 16pt corner radius, shadow(black/8%, radius 8, y 4), 20pt padding.

**Loading states:** Multi-phase progress with icons — "Scanning room...", "Extracting measurements...", "Generating build list...", "Applying regional pricing..."

---

## Implementation Schedule

| Day | Focus | Key Files |
|-----|-------|-----------|
| 1 | Data export script + Xcode project + all data models | `export_app_data.py`, all `Models/*.swift`, `DesignTokens.swift` |
| 2 | Claude API client + prompt builder + parser | `ClaudeAPIClient.swift`, `ClaudePromptBuilder.swift`, `BuildListParser.swift` |
| 3 | Cost engine + base price database | `CostEngine.swift`, `BasePriceDatabase.swift` — test end-to-end with hardcoded room |
| 4 | RoomPlan integration + measurement extraction | `RoomScanView.swift`, `RoomMeasurementExtractor.swift` — test on-device |
| 5 | Fallback: manual entry + photo capture | `ManualRoomEntryView.swift`, `PhotoCaptureView.swift`, `ScanMethodPickerView.swift` |
| 6 | ViewModel + navigation + input screens | `EstimateViewModel.swift`, `ProjectDescriptionView.swift`, `LocationPickerView.swift` |
| 7 | Results screen | `EstimateResultView.swift`, `LineItemListView.swift`, `EstimateSummaryCard.swift`, `Model3DPreviewView.swift` |
| 8 | PDF export | `PDFExporter.swift` |
| 9-10 | Polish + testing | Dark mode, edge cases, loading states, real-device LiDAR testing |

---

## Verification Checklist

1. **Claude prompt → parse**: Send "full bathroom remodel" for a 12×15ft room → verify JSON parses with realistic items (tile, vanity, toilet, plumbing, labor hours)
2. **CCI pricing**: Same build list priced for TX vs NY → NY should be 15-30% more expensive
3. **RoomPlan extraction**: Scan a real room → floor area within 5% of tape-measured actual
4. **End-to-end**: LiDAR scan → "repaint walls" → build list → priced estimate → PDF
5. **Fallback**: Same flow on non-LiDAR iPhone using photo + manual entry
6. **3D model**: USDZ exports and opens in QuickLook
7. **All 5 project types**: Each type produces appropriate materials and cost multiplier
