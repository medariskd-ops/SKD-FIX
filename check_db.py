from database import supabase

def check_schema():
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        if res.data:
            cols = list(res.data[0].keys())
            print("Columns in 'users':", cols)
            if "angkatan" in cols:
                print("SUCCESS: 'angkatan' column found in 'users'.")
            else:
                print("FAILURE: 'angkatan' column NOT found in 'users'.")
        else:
            print("Table 'users' is empty. Cannot verify columns via data.")
    except Exception as e:
        print("Error checking 'users':", e)

    try:
        res = supabase.table("scores").select("*").limit(1).execute()
        if res.data:
            print("Columns in 'scores':", list(res.data[0].keys()))
        else:
            print("Table 'scores' is empty.")
    except Exception as e:
        print("Error checking 'scores':", e)

if __name__ == "__main__":
    check_schema()
