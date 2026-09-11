"""DentiFlow Comprehensive Verification Test"""
from app import create_app

app = create_app()
app.config['TESTING'] = True

with app.test_client() as c:
    print("=" * 60)
    print("DENTIFLOW COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    results = []

    def check(num, desc, status, expect):
        ok = status in (expect if isinstance(expect, (list, tuple)) else [expect])
        tag = "PASS" if ok else "FAIL"
        print(f"[{num:>2}] {desc}: {status} -> {tag}")
        results.append(ok)

    # Public routes
    check(1, "Landing Page GET /", c.get('/').status_code, 200)
    check(2, "Login Page GET /login", c.get('/login').status_code, 200)
    check(3, "Register Page GET /register", c.get('/register').status_code, 200)
    check(4, "Forgot Password GET /forgot-password", c.get('/forgot-password').status_code, 200)
    check(5, "Doctors Directory GET /doctors/", c.get('/doctors/').status_code, 200)

    # Admin login
    r = c.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=False)
    check(6, "Admin Login POST /login", r.status_code, [302, 200])

    # Admin routes
    check(7, "Dashboard GET /dashboard", c.get('/dashboard', follow_redirects=True).status_code, 200)
    check(8, "Patients GET /patients/", c.get('/patients/').status_code, 200)
    check(9, "Appointments GET /appointments/", c.get('/appointments/').status_code, 200)
    check(10, "Clinical GET /clinical/", c.get('/clinical/').status_code, 200)
    check(11, "Billing GET /billing/", c.get('/billing/').status_code, 200)
    check(12, "Inventory GET /inventory/", c.get('/inventory/').status_code, 200)
    check(13, "Reports GET /reports/", c.get('/reports/').status_code, 200)
    check(14, "Settings GET /settings/", c.get('/settings/').status_code, 200)
    check(15, "Queue GET /queue/", c.get('/queue/').status_code, 200)
    check(16, "Treatments GET /treatments/", c.get('/treatments/').status_code, 200)

    # Logout
    check(17, "Logout GET /logout", c.get('/logout', follow_redirects=False).status_code, [302, 200])

    # Patient login + RBAC
    r = c.post('/login', data={'username': 'patient1', 'password': 'patient123'}, follow_redirects=False)
    check(18, "Patient Login POST /login", r.status_code, [302, 200])
    check(19, "Patient Portal GET /portal/", c.get('/portal/', follow_redirects=True).status_code, 200)
    check(20, "RBAC: Patient -> Settings = 403", c.get('/settings/').status_code, 403)

    # Doctor login
    c.get('/logout')
    r = c.post('/login', data={'username': 'dr.smith', 'password': 'doctor123'}, follow_redirects=False)
    check(21, "Doctor Login POST /login", r.status_code, [302, 200])
    check(22, "Doctor Dashboard GET", c.get('/doctors/dashboard', follow_redirects=True).status_code, 200)

    # Password reset flow
    c.get('/logout')
    check(23, "Forgot Password POST (enum protection)", c.post('/forgot-password', data={'email': 'fake@test.com'}, follow_redirects=True).status_code, 200)

    passed = sum(results)
    total = len(results)
    print()
    print("=" * 60)
    pct = int(passed / total * 100) if total else 0
    print(f"RESULTS: {passed}/{total} PASSED ({pct}%)")
    if passed == total:
        print("STATUS: ALL TESTS PASSED")
    else:
        print("STATUS: SOME TESTS FAILED")
    print("=" * 60)
