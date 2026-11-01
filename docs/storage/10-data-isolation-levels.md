# Transaction Isolation Levels

PostgreSQL uses READ COMMITTED by default. Graph analytics batch exports use REPEATABLE READ to guarantee point-in-time graph consistency.
