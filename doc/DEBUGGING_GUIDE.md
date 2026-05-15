# Scanner Issues Analysis & Fixes

## ✅ Issue 1: Duplicate `--crawl-depth` Argument (FIXED)

### Problem
```
argparse.ArgumentError: argument --crawl-depth: conflicting option string: --crawl-depth
```

### Root Cause
The `--crawl-depth` argument was defined **twice** in `src/web_scanner/main.py`:
- First definition: Lines 132-138
- Second definition: Lines 148-153 (removed)

### Solution
Removed the duplicate definition at lines 148-153.

### Verification
The argument now appears only once in the main parser. Command should now run without argparse errors.

---

## ⚠️ Issue 2: Authentication Not Detecting Vulnerabilities  

### Problem
When running authenticated scans against DVWA with:
```bash
python main.py --url http://localhost:8080 --auth-url /login.php --auth-user admin --auth-pass password
```
The scanner finds no vulnerabilities in authenticated areas.

### Root Causes (Potential)

1. **Form Field Detection Mismatch**
   - Default expected fields: `username`, `password`
   - DVWA uses: `user`, `pass`
   - The session_manager auto-detects these by input type, but this could fail

2. **Authentication Success Detection**
   - Looks for keywords: "dashboard", "welcome", "profile", "account", "logged in", "authenticated"
   - Defaults to "assume success" if none found
   - DVWA main page might not contain these keywords

3. **Active Tests Gate**
   - Active injection tests (which find real vulnerabilities) only run if:
     - `active_tests` is True (enabled by default)
     - `self.active_tests` is set in the config
   - Possible issue: `active_tests` might not be properly passed through config

4. **Authenticated Session Cookie Handling**
   - Cookies are stored in `session_manager.auth_state["cookies"]`
   - But the actual aiohttp session's cookie_jar is what matters
   - If session is closed/recreated, cookies might be lost

### Debugging Steps

1. **Test authentication separately:**
   ```bash
   python debug_auth.py --url http://localhost:8080 \
     --auth-url /login.php \
     --auth-user admin \
     --auth-pass password
   ```

2. **Check session manager logs:**
   - Add `--verbose` flag for DEBUG logging
   - Look for "Authenticated session established" message

3. **Test with forced credentials:**
   - Ensure you're using correct field names for your target
   - Consider adding `--auth-user-field` and `--auth-pass-field` arguments if not auto-detecting

---

## ⚠️ Issue 3: Identical Risk Score of 50 for Both DVWA & Juice Shop

### Problem
Both targets report risk score of 50, which is suspiciously identical.

### Root Cause Analysis

The risk score of 50 could come from:
- **Calculation 1** (vulnerability_scanner.py): 
  - Sum of `(severity_weight × confidence_weight)` for each finding
  - Example: 2 high-severity + high-confidence findings = 4.0 × 1.0 × 2 = 8.0 (not 50)

- **Calculation 2** (findings_processor.py):
  - `(critical × 40) + (high × 20) + (medium × 10) + (low × 2)`
  - Score of 50 = 5 medium findings OR 2 high + some low findings

- **Calculation 3** (report_generator.py):
  - Similar to vulnerability_scanner.py but might be calculating differently

### Hypothesis
The identical score suggests:
- Either **no findings are being detected** and a default/fallback score is being used
- Or **both targets have exactly the same finding distribution** (unlikely)
- Or **a default risk score is hardcoded** somewhere

### Investigation Needed
1. Check if findings list is empty: `len(results.get('findings', []))`
2. Verify risk score calculation function being used
3. Check for any hardcoded fallback values
4. Enable verbose logging to see what findings are being detected

---

## Recommended Solutions

### For Authentication Issue:
1. Add optional arguments for field name overrides:
   ```bash
   python main.py --url http://localhost:8080 \
     --auth-url /login.php \
     --auth-user admin \
     --auth-pass password \
     --auth-user-field "user" \
     --auth-pass-field "pass"
   ```

2. Add detailed auth logging to understand why findings aren't detected

3. Test basic vulnerable endpoints directly to ensure they're accessible

### For Risk Score Issue:
1. Log the raw findings before and after risk calculation
2. Verify that risk calculation is actually being performed
3. Check if there's a minimum/default risk score being applied
4. Ensure both targets are actually generating findings

---

## Testing Commands

### Test 1: Basic scan without auth
```bash
python main.py --url http://localhost:3000 --format json --output test_basic.json --verbose
```

### Test 2: Scan with auth
```bash
python main.py --url http://localhost:8080 \
  --auth-url /login.php \
  --auth-user admin \
  --auth-pass password \
  --format json --output test_auth.json --verbose
```

### Test 3: Debug auth flow
```bash
python debug_auth.py --url http://localhost:8080 \
  --auth-url /login.php \
  --auth-user admin \
  --auth-pass password
```

### Test 4: Check Juice Shop
```bash
python main.py --url http://localhost:3000 \
  --format json --output juice_shop.json --verbose
```

---

## Next Steps

1. Run debug_auth.py to see detailed scan flow
2. Check verbose logs for authentication messages
3. Verify findings are being detected
4. Identify which risk calculation is being used
5. Check if finding detection is the issue or risk scoring
