from database import supabase

def check_schema():
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        if res and hasattr(res, "data") and res.data:
            print("Columns in 'users':", list(res.data[0].keys()))
        else:
            print("Table 'users' is empty or no data returned.")
    except Exception as e:
        print("Error checking 'users':", e)

    try:
        res = supabase.table("scores").select("*").limit(1).execute()
        if res and hasattr(res, "data") and res.data:
            print("Columns in 'scores':", list(res.data[0].keys()))
        else:
            print("Table 'scores' is empty or no data returned.")
    except Exception as e:
        print("Error checking 'scores':", e)

if __name__ == "__main__":
    check_schema()
