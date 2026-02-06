from database import supabase

def check_schema():
    try:
        res = supabase.table("users").select("*").limit(1).execute()
        if res.data:
            print("Columns in 'users':", list(res.data[0].keys()))
        else:
            print("Table 'users' is empty.")
            # Try to insert and see if it fails differently or check PostgREST OpenAPI if available
            # But let's assume it's empty.
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
