# Python API

### Core Technologies & Principles
1. **Database Backend**:
    - Supports MySQL and SQLite via SQLAlchemy ORM
    - Uses SQLAlchemy declarative base for model definitions
    - Schema versioning with `SchemaVersion` table

2. **Architecture**:
    - Provider pattern (`RCDBProvider` as main access point)
    - Modular update system with plugin architecture
    - Type-safe condition value handling through `ConditionType`

3. **Key Libraries**:
    - SQLAlchemy for database abstraction
    - Click for CLI interface
    - Flask for web interface
    - Ply for query parsing

4. **Core Principles**:
    - Run-centric data model
    - Type-safe condition storage
    - Audit logging through `LogRecord` table
    - File versioning with SHA256 hashes

### Key Components

#### 1. Data Model (model.py)
```python
class Run(Base):
    __tablename__ = 'runs'
    number = Column(Integer, primary_key=True)
    conditions = relationship("Condition", back_populates="run")

class ConditionType(Base):
    value_type = Column(Enum(JSON_FIELD, STRING_FIELD, ...))

class Condition(Base):
    run_number = Column(Integer, ForeignKey('runs.number'))
    text_value = Column(Text)
    int_value = Column(Integer)
    # ... other type-specific fields
```

#### 2. Core Provider (provider.py)
```python
class RCDBProvider:
    def connect(self, connection_string):
        self.engine = create_engine(connection_string)
        self.session = sessionmaker(bind=self.engine)()

    def create_run(self, number):
        run = Run(number=number)
        self.session.add(run)
        return run

    def add_condition(self, run, key, value, replace=False):
        # Type-safe value handling
        ctype = self.get_condition_type(key)
        condition = Condition(type=ctype, run=run)
        condition.value = ctype.convert_value(value)
```

#### 3. Query System
```python
# Complex condition queries
result = db.select_values(
    ['beam_current', 'polarization_angle'],
    "run_type=='PHYSICS' and beam_energy>8.0",
    run_min=10000,
    run_max=20000
)

# Direct SQLAlchemy access
query = db.session.query(Run).join(Condition)
```

### Key Functions/Methods

#### Data Storage
```python
# Create run and add conditions
run = db.create_run(12345)
db.add_condition(run, "beam_energy", 8.5)
db.add_condition(run, "target_type", "LH2")

# Bulk operations
db.add_conditions(run, [
    ("event_count", 1500000),
    ("is_valid", True)
])

# File versioning
db.add_configuration_file(run, "/path/to/config.conf")
```

#### Data Retrieval
```python
# Get single run
run = db.get_run(12345)
print(run.conditions["beam_energy"].value)

# Complex queries
results = db.select_values(
    ["beam_current", "event_count"],
    "polarization_angle>0 and status=='VALID'",
    run_min=10000,
    run_max=20000
)
```

#### Update System
```python
# CODA log parsing
parse_result = coda_parser.parse_file("run_12345.log")
update_coda_conditions(db, parse_result)

# EPICS updates
epics_conditions = update_beam_conditions(run)
db.add_conditions(run, epics_conditions)
```

### Performance Features
1. **Bulk Operations**:
    - `add_conditions()` for batch updates
    - SQLAlchemy session-based transactions

2. **Caching**:
    - Condition type caching
    - Run period caching

3. **Optimized Queries**:
    - Hybrid properties for common queries
    - Direct SQL access for complex operations

### CLI Interface (cli/app.py)
```bash
# Query runs
rcdb select "beam_current>50 and status=='VALID'" -v beam_current,run_type

# Database maintenance
rcdb db update  # Schema migrations
rcdb repair evio-files  # Fix file associations
```

### Key Design Patterns
1. **Unit of Work**:
    - SQLAlchemy session management
    - Atomic transactions for critical operations

2. **Strategy Pattern**:
    - Different update handlers (CODA/EPICS/ROC)
    - Pluggable condition types

3. **Observer Pattern**:
    - Update reasons (start/update/end)
    - Multi-system synchronization

### Typical Workflow
1. **Run Start**:
   ```python
   run = db.create_run(run_number)
   update_coda_conditions(db, coda_parse_result)
   update_epics_conditions(db, run)
   ```

2. **During Run**:
   ```python
   db.add_condition(run, "event_rate", current_rate)
   ```

3. **Run End**:
   ```python
   run.end_time = datetime.now()
   update_file_associations(run)
   db.session.commit()
   ```

The RCDB API combines database rigor with experimental physics needs, providing type safety, audit capabilities, and high-performance access patterns while maintaining flexibility for complex experimental conditions.