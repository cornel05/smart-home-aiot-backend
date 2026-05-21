# Graph Report - DADN  (2026-05-21)

## Corpus Check
- 54 files · ~20,969 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1038 nodes · 1838 edges · 89 communities (72 shown, 17 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 70 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `68b70134`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]

## God Nodes (most connected - your core abstractions)
1. `cn()` - 267 edges
2. `skillOverrides` - 20 edges
3. `evaluate()` - 18 edges
4. `parse_serial_frame()` - 15 edges
5. `_make_pty()` - 14 edges
6. `nums` - 13 edges
7. `TestParseSerialFrame` - 13 edges
8. `_run_thread_until_eof()` - 13 edges
9. `buttonVariants` - 13 edges
10. `LCD1602` - 12 edges

## Surprising Connections (you probably didn't know these)
- `LSTMModel` --uses--> `SensorTelemetry`  [INFERRED]
  ai/data_pipeline.py → database/models.py
- `CommandRequest` --uses--> `SystemEvent`  [INFERRED]
  api/routes_device.py → database/models.py
- `send_command()` --calls--> `SystemEvent`  [INFERRED]
  api/routes_device.py → database/models.py
- `TestManualOverrideFanOn` --uses--> `Base`  [INFERRED]
  tests/test_integration_manual_override.py → database/models.py
- `TestManualOverrideFanOn` --uses--> `NodeMetadata`  [INFERRED]
  tests/test_integration_manual_override.py → database/models.py

## Communities (89 total, 17 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (35): Input(), Separator(), Sidebar(), SidebarContent(), SidebarContext, SidebarContextProps, SidebarFooter(), SidebarGroup() (+27 more)

### Community 1 - "Community 1"
Cohesion: 0.30
Nodes (10): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetFooter(), SheetHeader(), SheetOverlay(), SheetPortal() (+2 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (23): App(), router, Layout(), ImageWithFallback(), ActivityLogs(), CHART_DATA, getTypeStyles(), LOG_DATA (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.18
Nodes (14): Architecture, code:block1 (YoloBit (serial) ──► Gateway (Python) ──► MQTT Broker (Mosqu), code:python (I2C_SCL_PIN = 19), code:python (I2C_SCL_PIN = 20), code:python (I2C_SCL_PIN = 21), code:bash (# Full suite (no DB or broker required — SQLite in-memory)), code:block25 (.), code:env (ACTUATOR_PIN_MAP='{"fan":10,"light":13}') (+6 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (37): bh1750_thread(), BoardSerial, command_subscriber_thread(), dht11_thread(), format_serial_frame(), handle_command(), main(), make_client() (+29 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (24): begin, btn, element, end, getCellValue(), header, helpCheck, line_height (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (14): evaluate(), Evaluate sensor payload against rules. Returns list of triggered events., node_id absent in payload → falls back to settings.NODE_ID (1)., ir > 0 → ir_motion event returned (no MQTT publish_command for IR)., temp > 26.0 (TEMP_FAN_THRESHOLD) → fan_activated event returned., temp > threshold → publish_command('fan', 'on', value=temp) called., temp == 26.0 is NOT > threshold → no fan event (rule uses strict >)., light_intensity < 200.0 → light_activated event returned. (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (8): formatValue(), SENSOR_META, SensorCard(), useSensorData(), App(), formatTimestamp(), makeLogs(), ROUTES

### Community 8 - "Community 8"
Cohesion: 0.20
Nodes (19): Command(), CommandDialog(), CommandEmpty(), CommandGroup(), CommandInput(), CommandItem(), CommandList(), CommandSeparator() (+11 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (33): build_board_command(), _make_pty(), Tests for gateway serial port reading: - parse_serial_frame unit tests (pure, no, Return (master_fd, slave_path). Caller owns both fds., Start serial_read_thread; close master after *delay* seconds to cause EOF., Return (master_fd, slave_path). Caller owns both fds., Start serial_read_thread; close master after *delay* seconds to cause EOF., Write a valid frame in two chunks; readline should reassemble. (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.21
Nodes (16): Menubar(), MenubarCheckboxItem(), MenubarContent(), MenubarGroup(), MenubarItem(), MenubarLabel(), MenubarMenu(), MenubarPortal() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (15): ContextMenu(), ContextMenuCheckboxItem(), ContextMenuContent(), ContextMenuGroup(), ContextMenuItem(), ContextMenuLabel(), ContextMenuPortal(), ContextMenuRadioGroup() (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (13): 16. User Interface Design, 1. Project Topic, 2. Team Members, 3. Teamwork Methodology, 5. Device Specifications, 9.1 Hardware Sensor Layer, 9.2 Communication & Network Resilience, 9. Non-Functional Requirements (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.22
Nodes (15): DropdownMenu(), DropdownMenuCheckboxItem(), DropdownMenuContent(), DropdownMenuGroup(), DropdownMenuItem(), DropdownMenuLabel(), DropdownMenuPortal(), DropdownMenuRadioGroup() (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (8): _make_sensor_row(), GET /api/sensors/latest → one merged snapshot with all required keys., temperature=32.5 (>30°C) and light=150.0 (<200 Lux) stored correctly., limit=1 query param — route accepts it without error., limit > 100 violates le=100 constraint → 422., minutes > 1440 violates le=1440 → 422., TestGetSensorsHistory, TestGetSensorsLatest

### Community 15 - "Community 15"
Cohesion: 0.27
Nodes (12): FormControl(), FormDescription(), FormField(), FormFieldContext, FormFieldContextValue, FormItem(), FormItemContext, FormItemContextValue (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.25
Nodes (7): Base, NodeMetadata, SensorTelemetry, SystemEvent, DeclarativeBase, GET /api/devices/events → list of event dicts., TestGetDeviceEvents

### Community 17 - "Community 17"
Cohesion: 0.11
Nodes (21): Avatar(), AvatarFallback(), AvatarImage(), Card(), CardAction(), CardContent(), CardDescription(), CardFooter() (+13 more)

### Community 19 - "Community 19"
Cohesion: 0.15
Nodes (7): POST /api/devices/fan/command with valid body → 200 + correct JSON., POST fan/on → publish_command('fan', 'on', 32.0) called exactly once., POST fan/on → db.add() and db.commit() both called., POST light/on with low-light value → publish_command('light', 'on', 150.0)., value is optional — POST with no value still succeeds., node_id in body overrides settings.NODE_ID., TestPostDeviceCommand

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (13): 13.1 Database Engine Selection, 13.2 Schema Design and Structure, 13.3 Hypertable Partitioning Mechanism, 13.4 Entity-Relationship Modeling, 13.5 Mock Data Validation, 13. Database Architecture and Implementation, actuator_logs Table, Benefits (+5 more)

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (12): code:text (TEMP:25.3,HUM:61.5,LIGHT:430,IR:0), code:text (CMD:{device},{state}), code:text (DHT20   -> I2C port), code:python (I2C_SCL_PIN = 19), code:python (I2C_SCL_PIN = 20), code:python (I2C_SCL_PIN = 21), code:text (56), code:python (LCD_ADDR = 0x27) (+4 more)

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (10): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartStyle(), ChartTooltipContent(), getPayloadConfigFromPayload() (+2 more)

### Community 23 - "Community 23"
Cohesion: 0.30
Nodes (10): Drawer(), DrawerClose(), DrawerContent(), DrawerDescription(), DrawerFooter(), DrawerHeader(), DrawerOverlay(), DrawerPortal() (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.17
Nodes (12): 11.1 Physical Layer Configuration, 11.2.1 Data Frame Protocol and Cloud Integration, 11.2.2 Implementation Challenges and Optimization, 11.2 IoT Gateway Architecture, 11. Hardware Integration and IoT Gateway, code:text (TEMP:{temp},HUM:{hum},LIGHT:{light},IR:{ir}), code:python (import serial), Hardware Interface Mapping (+4 more)

### Community 25 - "Community 25"
Cohesion: 0.22
Nodes (8): 1. Kiến trúc, 2. HW Components, 3. Tasks / Functions, 4. YoloFarm Integration Targets, 5. What YoloFarm Agent Need Know, Open Questions, Priority Files, YoloHome Context Package

### Community 26 - "Community 26"
Cohesion: 0.35
Nodes (9): NavigationMenu(), NavigationMenuContent(), NavigationMenuIndicator(), NavigationMenuItem(), NavigationMenuLink(), NavigationMenuList(), NavigationMenuTrigger(), navigationMenuTriggerStyle (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (12): client_and_mqtt(), db_session(), Integration test: Manual Override flow (Module 3).  Flow under test:   User clic, Backend publishes exactly one MQTT command with correct device/action., SystemEvent row persisted; trigger_source='manual', event_type='fan_on'., Manual override bypasses automatic rule evaluation entirely., Single POST → exactly one DB row; no duplicate logging., SQLite in-memory DB with the real SQLAlchemy schema.     Seeds node_metadata.nod (+4 more)

### Community 28 - "Community 28"
Cohesion: 0.36
Nodes (8): Table(), TableBody(), TableCaption(), TableCell(), TableFooter(), TableHead(), TableHeader(), TableRow()

### Community 29 - "Community 29"
Cohesion: 0.20
Nodes (10): 7.1 Wiring Design & Sensor Testing, 7.2 MQTT Gateway & Pub/Sub Testing, 7. Hardware Selection and Integration Plan, Main Tasks, MQTT Gateway Setup, Pub/Sub Testing, Publishing, Result (+2 more)

### Community 30 - "Community 30"
Cohesion: 0.39
Nodes (7): Breadcrumb(), BreadcrumbEllipsis(), BreadcrumbItem(), BreadcrumbLink(), BreadcrumbList(), BreadcrumbPage(), BreadcrumbSeparator()

### Community 31 - "Community 31"
Cohesion: 0.18
Nodes (13): 1 — Infrastructure (DB + MQTT broker), 2 — Environment, 3 — Backend, 4 — Backend, 6 — Frontend, code:bash (uv sync), code:bash (sudo usermod -aG dialout "$USER"), code:bash (cd frontend) (+5 more)

### Community 32 - "Community 32"
Cohesion: 0.25
Nodes (8): 12.1 Real-Time Data Visualization, 12.2 Threshold-Based Automation Logic and Backend API, 12.3 System Pipeline Integration and Optimization, 12. Application Logic and Dashboard Interface, Example, Features, Git/GitHub Issues Resolved, Verified Pipeline

### Community 33 - "Community 33"
Cohesion: 0.36
Nodes (4): _on_message(), _payload_from_feed(), _persist(), _validate_payload()

### Community 34 - "Community 34"
Cohesion: 0.07
Nodes (42): AlertDialog(), AlertDialogAction(), AlertDialogCancel(), AlertDialogContent(), AlertDialogDescription(), AlertDialogFooter(), AlertDialogHeader(), AlertDialogOverlay() (+34 more)

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (7): 10.1 Use Case Diagrams, 10.2 Use Case Scenarios, 10.3 Sequence Diagrams, 10.4 Activity Diagrams, 10. System Modeling (UML Diagrams), UC Scenario 1: Read and Transmit Sensor Data, UC Scenario 2: Calibrate Sensor Baseline

### Community 37 - "Community 37"
Cohesion: 0.29
Nodes (7): 14.1 Integration Overview and Motivation, 14.2 LSTM-Based Predictive Algorithm, 14.3 Data Pipeline Architecture, 14.4 Current Implementation Status, 14. Artificial Intelligence Integration Strategy, Pipeline Steps, Preprocessing

### Community 38 - "Community 38"
Cohesion: 0.29
Nodes (7): 15.1 End-to-End Latency Assessment, 15.2 System Uptime Assessment, 15.3 Compliance Summary, 15. Performance and Requirements Verification, Reliability Mechanisms, Result, Result

### Community 39 - "Community 39"
Cohesion: 0.22
Nodes (11): 5 — Frontend, API Reference, code:text (I2C_SCAN:[56, ...]), code:python (import task_actuators), code:text ([ACTUATOR] fan=1), code:bash (# T1 — infra), code:bash (curl -X POST http://localhost:8000/api/devices/fan/command \), Devices (+3 more)

### Community 40 - "Community 40"
Cohesion: 0.09
Nodes (32): files, z_10fae538ba4e8521___init___py, z_10fae538ba4e8521_routes_device_py, z_10fae538ba4e8521_routes_sensor_py, z_de3833460954761d___init___py, z_de3833460954761d_rule_engine_py, format, globals (+24 more)

### Community 43 - "Community 43"
Cohesion: 0.60
Nodes (4): Alert(), AlertDescription(), AlertTitle(), alertVariants

### Community 44 - "Community 44"
Cohesion: 0.31
Nodes (9): 3 — Yolo:Bit Firmware Upload With Pymakr, 4 — Gateway, code:text (TEMP:25.3,HUM:61.5,LIGHT:430,IR:0), code:text (CMD:{device},{state}), code:text (firmware/yolobit/yolobit.code-workspace), code:text (main.py), Connect and upload, Install the correct Pymakr extension (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.33
Nodes (5): Button, Design system guidelines, General guidelines, Usage, Variants

### Community 46 - "Community 46"
Cohesion: 0.53
Nodes (4): Accordion(), AccordionContent(), AccordionItem(), AccordionTrigger()

### Community 47 - "Community 47"
Cohesion: 0.44
Nodes (5): ToggleGroup(), ToggleGroupContext, ToggleGroupItem(), Toggle(), toggleVariants

### Community 48 - "Community 48"
Cohesion: 0.33
Nodes (5): 1. Start infra, 2. Start backend, 3. Start gateway (separate terminal), 4. Start frontend, smart-home-aiot-backend

### Community 49 - "Community 49"
Cohesion: 0.40
Nodes (4): client(), mock_db(), httpx AsyncClient pointed at the FastAPI app.     - get_db overridden with mock_, Fully mocked AsyncSession — no real DB needed.

### Community 50 - "Community 50"
Cohesion: 0.60
Nodes (3): Collapsible(), CollapsibleContent(), CollapsibleTrigger()

### Community 51 - "Community 51"
Cohesion: 0.40
Nodes (5): 6.1 Table 1: Node Metadata, 6.2 Table 2: Sensor Telemetry, 6.3 Table 3: System Events, 6.4 Data Analytics Strategy, 6. Database Architecture

### Community 52 - "Community 52"
Cohesion: 0.40
Nodes (5): FACULTY OF COMPUTER SCIENCE AND ENGINEERING, MULTIDISCIPLINARY PROJECT, Smart Home Automation with AIoT — Week 2 Report, UNIVERSITY OF TECHNOLOGY, VIETNAM NATIONAL UNIVERSITY, HO CHI MINH CITY

### Community 53 - "Community 53"
Cohesion: 0.07
Nodes (26): dependencies, axios, react, react-dom, recharts, tailwindcss, @tailwindcss/vite, devDependencies (+18 more)

### Community 54 - "Community 54"
Cohesion: 0.50
Nodes (3): Expanding the ESLint configuration, React Compiler, React + Vite

### Community 60 - "Community 60"
Cohesion: 0.67
Nodes (3): 4. Functional Branch Division, CE Member, CS Members

### Community 61 - "Community 61"
Cohesion: 0.67
Nodes (3): 8.1 Hardware Sensor Layer, 8.2 Communication & Core Modules, 8. Detailed Functional Requirements

### Community 76 - "Community 76"
Cohesion: 0.09
Nodes (22): permissions, allow, skillOverrides, caveman-commit, caveman-compress, caveman-help, caveman-review, clean_instruction (+14 more)

### Community 77 - "Community 77"
Cohesion: 0.53
Nodes (4): Popover(), PopoverAnchor(), PopoverContent(), PopoverTrigger()

### Community 78 - "Community 78"
Cohesion: 0.53
Nodes (4): InputOTP(), InputOTPGroup(), InputOTPSeparator(), InputOTPSlot()

### Community 79 - "Community 79"
Cohesion: 0.07
Nodes (24): extract(), LSTMModel, CommandRequest, get_events(), send_command(), get_history(), get_latest(), BaseModel (+16 more)

### Community 80 - "Community 80"
Cohesion: 0.40
Nodes (5): 5 — Gateway, code:bash (python gateway/gateway.py), code:bash (python gateway/gateway.py --port /dev/ttyUSB0), code:block19 (TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0), code:block20 (CMD:{device},{state})

### Community 81 - "Community 81"
Cohesion: 0.53
Nodes (4): Tabs(), TabsContent(), TabsList(), TabsTrigger()

### Community 84 - "Community 84"
Cohesion: 0.67
Nodes (3): SMART HOME AUTOMATION WITH AIoT, Students, Week 2 Report

## Knowledge Gaps
- **194 isolated node(s):** `PreToolUse`, `allow`, `caveman-commit`, `caveman-compress`, `caveman-help` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cn()` connect `Community 17` to `Community 0`, `Community 1`, `Community 8`, `Community 10`, `Community 11`, `Community 13`, `Community 15`, `Community 22`, `Community 23`, `Community 26`, `Community 28`, `Community 30`, `Community 34`, `Community 43`, `Community 46`, `Community 47`, `Community 77`, `Community 78`, `Community 79`, `Community 81`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `Select()` connect `Community 79` to `Community 27`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Why does `publish_command()` connect `Community 79` to `Community 6`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `evaluate()` (e.g. with `_on_message()` and `publish_command()`) actually correct?**
  _`evaluate()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `parse_serial_frame()` (e.g. with `test_serial_frame_format_is_strict()` and `.test_valid_frame_returns_correct_dict()`) actually correct?**
  _`parse_serial_frame()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PreToolUse`, `allow`, `caveman-commit` to the rest of the system?**
  _263 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.09435707678075855 - nodes in this community are weakly interconnected._