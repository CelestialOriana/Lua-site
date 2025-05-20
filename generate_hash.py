import bcrypt # type: ignore

# Générer un hash pour "admin123"
admin_password = "admin123".encode('utf-8')
admin_hash = bcrypt.hashpw(admin_password, bcrypt.gensalt())
print("Hash pour admin123:", admin_hash.decode('utf-8'))

# Générer un hash pour "user123"
user_password = "user123".encode('utf-8')
user_hash = bcrypt.hashpw(user_password, bcrypt.gensalt())
print("Hash pour user123:", user_hash.decode('utf-8'))