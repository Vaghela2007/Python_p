# PTMAE Documentation

## Architecture
```
+----------+     +----------+     +-----------+
| Module 1 | --> | Module 2 | --> | Module 3  |
+----------+     +----------+     +-----------+
       |                                |
+----------+                      +-----------+
| Module 4 | <------------------- | Module 5  |
+----------+                      +-----------+
```
Account <- SavingsAccount, CurrentAccount, CreditAccount

## State and scope tracking
| Name | Kind | Where |
|---|---|---|
| audited | nonlocal | create_audit_filter |
| counter | global (avoided) | none |
| _Account__balance | mangled | Account |

## Module compliance checklist
- [x] Unit 1 loops and arithmetic
- [x] Unit 2 parser and closures
- [x] Unit 3 comprehensions
- [x] Unit 4 file I/O
- [x] Unit 5 OOP
