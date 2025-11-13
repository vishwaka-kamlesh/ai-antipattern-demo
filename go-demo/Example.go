package main

import "database/sql"

func badLoop(db *sql.DB) {
	for i := 0; i < 10; i++ {
		db.Query("SELECT * FROM users WHERE id = ?", i)
	}
}
