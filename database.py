import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_database()
        
    def create_tables(self):
        # Users table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            phone INTEGER
        )
        """)
        
        # Records table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_exp TEXT NOT NULL,
            city_exp TEXT NOT NULL,
            phone_exp TEXT NOT NULL,
            name_dest TEXT NOT NULL,
            phone_dest TEXT NOT NULL,
            city_dest TEXT NOT NULL,
            nmbr_package INTEGER NOT NULL,
            gender_package TEXT NOT NULL,
            value_package REAL NOT NULL,
            kilos REAL NOT NULL,
            price REAL NOT NULL,
            created_at TEXT NOT NULL,
            modified_at TEXT,
            status TEXT
        )
        """)
        
        # Modification log table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS modification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER,
            action_type TEXT,
            details TEXT,
            modified_at TEXT,
            FOREIGN KEY (record_id) REFERENCES records(id)
        )
        """)
        
        self.conn.commit()

    def insert_user(self, username, password, phone):
        self.cursor.execute("""
        INSERT INTO users (username, password, phone)
        VALUES (?, ?, ?)
        """, (username, password, phone))
        self.conn.commit()
        
    def get_user(self, username, password):
        self.cursor.execute("""
        SELECT * FROM users 
        WHERE username = ? AND password = ?
        """, (username, password))
        return self.cursor.fetchone()
    
    def insert_record(self, name_exp, city_exp, phone_exp, name_dest, phone_dest, city_dest, 
                     nmbr_package, gender_package, value_package, kilos, price):
        try:
            self.cursor.execute("""
            INSERT INTO records (
                name_exp, city_exp, phone_exp, name_dest, phone_dest, city_dest,
                nmbr_package, gender_package, value_package, kilos, price, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name_exp, city_exp, phone_exp, name_dest, phone_dest, city_dest,
                nmbr_package, gender_package, value_package, kilos, price, 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            self.conn.commit()
            return self.cursor.lastrowid  # Retourne l'ID du dernier enregistrement inséré
        except Exception as e:
            print(f"Error inserting record: {str(e)}")
            self.conn.rollback()
            raise
    
    def get_all_records(self):
        self.cursor.execute("SELECT * FROM records ORDER BY id DESC")
        return self.cursor.fetchall()
        
    def search_records(self, search_text):
        self.cursor.execute("""
            SELECT * FROM records 
            WHERE id LIKE ? OR name_exp LIKE ? 
            ORDER BY id DESC
        """, (f"%{search_text}%", f"%{search_text}%"))
        return self.cursor.fetchall()
        
    def update_record(self, record_id, data):
        """Update an existing record in the database."""
        try:
            # Validate record exists
            record = self.get_record(record_id)
            if not record:
                print(f"Record {record_id} not found")
                return False

            # Validate data
            is_valid, message = self.validate_record_data(data)
            if not is_valid:
                print(f"Invalid data: {message}")
                return False

            # Convert string values to appropriate types
            try:
                nmbr_package = int(data['nmbr_package'])
                value_package = float(data['value_package'])
                kilos = float(data['kilos'])
                price = float(data['price'])
            except ValueError as e:
                print(f"Error converting values: {e}")
                return False

            # Update the record
            self.cursor.execute("""
                UPDATE records 
                SET name_exp=?, 
                    city_exp=?, 
                    phone_exp=?, 
                    name_dest=?, 
                    phone_dest=?, 
                    city_dest=?,
                    nmbr_package=?, 
                    gender_package=?, 
                    value_package=?,
                    kilos=?, 
                    price=?,
                    modified_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                data['name_exp'], 
                data['city_exp'], 
                data['phone_exp'],
                data['name_dest'], 
                data['phone_dest'], 
                data['city_dest'],
                nmbr_package, 
                data['gender_package'], 
                value_package,
                kilos, 
                price, 
                record_id
            ))
            
            # Log the modification
            self.cursor.execute("""
                INSERT INTO modification_log (record_id, action_type)
                VALUES (?, 'update')
            """, (record_id,))
            
            self.conn.commit()
            print(f"Record {record_id} updated successfully")
            return True
        
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Error updating record: {e}")
            self.conn.rollback()
            return False

    def log_modification(self, record_id, action_type):
        """Log modifications to records."""
        try:
            self.cursor.execute("""
                INSERT INTO modification_log (record_id, action_type)
                VALUES (?, ?)
            """, (record_id, action_type))
            
            self.conn.commit()
        except Exception as e:
            print(f"Error logging modification: {e}")

    def get_record_modifications(self, record_id):
        """Get modification history for a record."""
        try:
            self.cursor.execute("""
                SELECT action_type, modified_at 
                FROM modification_log 
                WHERE record_id=? 
                ORDER BY modified_at DESC
            """, (record_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting modification history: {e}")
            return []

    def get_record(self, record_id):
        """Get a single record by ID."""
        try:
            self.cursor.execute("""
                SELECT * FROM records WHERE id=?
            """, (record_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting record: {e}")
            return None

    def validate_record_data(self, data):
        """Validate record data before update or insert."""
        required_fields = [
            'name_exp', 'city_exp', 'phone_exp',
            'name_dest', 'phone_dest', 'city_dest',
            'nmbr_package', 'gender_package', 'value_package',
            'kilos', 'price'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Le champ {field} est requis"
        
        # Validate numeric fields
        try:
            int(data['nmbr_package'])
            float(data['value_package'])
            float(data['kilos'])
            float(data['price'])
        except ValueError:
            return False, "Les valeurs numériques sont invalides"
        
        # Validate phone numbers
        if not (data['phone_exp'].isdigit() and data['phone_dest'].isdigit()):
            return False, "Les numéros de téléphone doivent contenir uniquement des chiffres"
        
        return True, "Données valides"

    def delete_record(self, record_id):
        try:
            self.cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False
            
    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def migrate_database(self):
        """Add missing columns to existing tables"""
        try:
            # Vérifier et ajouter les colonnes manquantes dans records
            try:
                self.cursor.execute("SELECT modified_at FROM records LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE records ADD COLUMN modified_at TEXT")
                print("Colonne modified_at ajoutée à records")

            try:
                self.cursor.execute("SELECT status FROM records LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE records ADD COLUMN status TEXT")
                print("Colonne status ajoutée à records")

            # Vérifier et ajouter les colonnes manquantes dans modification_log
            try:
                self.cursor.execute("SELECT details FROM modification_log LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE modification_log ADD COLUMN details TEXT")
                print("Colonne details ajoutée à modification_log")

            try:
                self.cursor.execute("SELECT modified_at FROM modification_log LIMIT 1")
            except sqlite3.OperationalError:
                self.cursor.execute("ALTER TABLE modification_log ADD COLUMN modified_at TEXT")
                print("Colonne modified_at ajoutée à modification_log")

            self.conn.commit()
            print("Migration de la base de données terminée avec succès")
        except Exception as e:
            print(f"Erreur lors de la migration: {str(e)}")
            self.conn.rollback()

    def modify_record(self, record_id, data):
        """Modify an existing record in the database with logging."""
        try:
            # Vérifier si l'enregistrement existe
            current_record = self.get_record(record_id)
            if not current_record:
                return False, "Enregistrement non trouvé"

            # Valider les données
            try:
                nmbr_package = int(data['nmbr_package'])
                value_package = float(data['value_package'])
                kilos = float(data['kilos'])
                price = float(data['price'])
            except ValueError:
                return False, "Valeurs numériques invalides"

            # Vérifier les numéros de téléphone
            if not (data['phone_exp'].isdigit() and data['phone_dest'].isdigit()):
                return False, "Les numéros de téléphone doivent être numériques"

            # Mettre à jour l'enregistrement
            self.cursor.execute("""
                UPDATE records 
                SET name_exp = ?,
                    city_exp = ?,
                    phone_exp = ?,
                    name_dest = ?,
                    phone_dest = ?,
                    city_dest = ?,
                    nmbr_package = ?,
                    gender_package = ?,
                    value_package = ?,
                    kilos = ?,
                    price = ?,
                    modified_at = CURRENT_TIMESTAMP,
                    status = 'Modifié'
                WHERE id = ?
            """, (
                data['name_exp'],
                data['city_exp'],
                data['phone_exp'],
                data['name_dest'],
                data['phone_dest'],
                data['city_dest'],
                nmbr_package,
                data['gender_package'],
                value_package,
                kilos,
                price,
                record_id
            ))

            # Enregistrer la modification dans le journal
            self.cursor.execute("""
                INSERT INTO modification_log (
                    record_id,
                    action_type,
                    modified_at,
                    details
                ) VALUES (?, ?, CURRENT_TIMESTAMP, ?)
            """, (
                record_id,
                'MODIFICATION',
                f"Modifié par l'utilisateur - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ))

            self.conn.commit()
            return True, "Modification r��ussie"

        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Erreur SQLite: {str(e)}"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erreur: {str(e)}"
