# test_what_has_circumference.py

from fetcher import Fetcher

if __name__ == "__main__":
    fetcher = Fetcher()
    
    f = Fetcher()
    print(f.fetch_cosmic_object("Earth"))
    print(f.fetch_cosmic_object("Moon"))
    print(f.fetch_cosmic_object("Saturn"))

    