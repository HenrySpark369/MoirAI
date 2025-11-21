# 🧪 Logout Test Suite - Complete Guide

## 📋 Overview

La suite de tests de logout es un conjunto completo de herramientas para diagnosticar problemas con el logout en todos los roles de usuario (Student, Company, Admin).

**Características principales:**
- ✅ Crea cuentas temporales para cada rol
- ✅ Ejecuta flujo completo: Register → Login → Logout
- ✅ Captura TODOS los errores de consola DevTools
- ✅ Captura errores de red
- ✅ Guarda logs en localStorage para análisis posterior
- ✅ Interfaz web visual para ver resultados en tiempo real
- ✅ Exporta reports en JSON y TXT

---

## 🚀 Quick Start

### Opción 1: Web Interface (Recomendada)

1. **Inicia el servidor:**
```bash
cd /Users/sparkmachine/MoirAI
python main.py
# o
uvicorn app.main:app --reload
```

2. **Accede a la página de tests:**
   - Abre en el navegador: `http://127.0.0.1:8000/logout-test`

3. **Haz clic en "Run All Tests"**

4. **Espera a que se completen todos los tests** (puede tomar 30-60 segundos)

5. **Revisa los resultados** - Verás en tiempo real:
   - ✅/❌ Estado de cada paso (Register, Login, Logout, etc.)
   - Console logs capturados
   - Errores específicos
   - Warnings

6. **Descarga el report** - Click en "Download JSON Report" o "Export Report"

---

### Opción 2: Console Manual

Si prefieres usar la consola de DevTools:

1. Abre `http://127.0.0.1:8000/logout-test`
2. Abre DevTools (F12 o Cmd+Option+I)
3. Ve a la pestaña "Console"
4. Copia y pega:

```javascript
await runFullLogoutTest()
```

5. Presiona Enter

Espera a que termine. Los resultados se guardan en localStorage.

6. Ver resultados:
```javascript
JSON.parse(localStorage.getItem('logoutTestReport'))
```

---

## 📊 Understanding the Report

### Structure

```json
{
  "timestamp": "2025-11-20T...",
  "results": {
    "student": {
      "role": "student",
      "register": {...},
      "login": {...},
      "getMe": {...},
      "logout": {...},
      "errors": ["Error 1", "Error 2"]
    },
    "company": {...},
    "admin": {...}
  },
  "logs": {
    "console": [...],
    "errors": [...],
    "warnings": [...]
  }
}
```

### Key Sections

**1. Register Result**
- Should return user_id and email
- If null/error = Registration failed

**2. Login Result**
- Should return access_token
- If null/error = Login failed

**3. GetMe Result**
- Should return user info (email, role, etc.)
- If null/error = User info retrieval failed

**4. Logout Result**
- Should return {"message": "Logged out successfully"}
- If null/error = **THIS IS YOUR PROBLEM** (Logout failing)

**5. Errors Array**
- Lists all errors encountered during the test
- Examples:
  - "Logout failed: ..."
  - "localStorage not cleared: api_key still present"

---

## 🔍 Troubleshooting

### Common Issues

#### Issue 1: "Logout failed: ..."
**Indicates:** Backend logout endpoint is having issues

**Solution:**
1. Check the error message in the report
2. Verify `/auth/logout` endpoint exists and works
3. Check backend logs for server errors
4. Verify authManager is calling the correct URL

#### Issue 2: "localStorage not cleared: api_key still present"
**Indicates:** Frontend not clearing localStorage after logout

**Solutions:**
1. Check if `authManager.logout()` is working
2. Verify `localStorage.removeItem()` is being called
3. Check for JavaScript errors in console

#### Issue 3: "Unhandled Promise Rejection"
**Indicates:** Promise error not being caught

**Solution:**
1. Look at the stack trace in the errors section
2. Add `.catch()` to promises
3. Check for syntax errors

#### Issue 4: One role fails but others pass
**Indicates:** Role-specific issue (backend role validation, auth, etc.)

**Solution:**
1. Check if the failing role is properly registered
2. Verify role permissions in backend
3. Check role-specific endpoints

---

## 📝 How to Fix Issues Found

### Step 1: Run Tests
```javascript
await runFullLogoutTest()
```

### Step 2: Analyze Report
```javascript
const report = JSON.parse(localStorage.getItem('logoutTestReport'))
// Check report.results.[role].errors
// Check report.logs.errors
```

### Step 3: Identify Problem
- Look for patterns
- Check which step fails first
- Note the exact error message

### Step 4: Fix Backend/Frontend
- If backend error: Fix `/auth/logout` endpoint
- If frontend error: Fix logout() function in JavaScript
- If localStorage issue: Check if clearing is happening

### Step 5: Re-run Tests
```javascript
localStorage.clear()  // Clear old results
await runFullLogoutTest()
```

### Step 6: Verify Fix
```javascript
const newReport = JSON.parse(localStorage.getItem('logoutTestReport'))
// Check if errors are gone
```

---

## 🔧 Debugging Tips

### View Full Error Details
```javascript
const report = JSON.parse(localStorage.getItem('logoutTestReport'))
const studentErrors = report.results.student.errors
studentErrors.forEach(err => console.log(err))
```

### View All Console Logs
```javascript
const report = JSON.parse(localStorage.getItem('logoutTestReport'))
report.logs.console.forEach(log => console.log(log.message))
```

### View Network Errors
```javascript
const report = JSON.parse(localStorage.getItem('logoutTestReport'))
report.logs.errors.forEach(err => console.log(err.message))
```

### Check Specific Role
```javascript
const report = JSON.parse(localStorage.getItem('logoutTestReport'))
console.log('Student logout status:', report.results.student.logout)
console.log('Company logout status:', report.results.company.logout)
console.log('Admin logout status:', report.results.admin.logout)
```

---

## 📂 Files Involved

### Test Suite Files
- **`app/frontend/static/js/logout-test-suite.js`**
  - Core test logic
  - API client simulation
  - Log capture system

- **`app/frontend/templates/logout-test.html`**
  - Web interface
  - Console display
  - Results visualization
  - Report export

### Endpoints Being Tested
```
POST /api/v1/auth/register    - User registration
POST /api/v1/auth/login       - User login
GET  /api/v1/auth/me          - Get user info
POST /api/v1/auth/logout      - User logout (THE KEY ONE)
```

---

## ✅ Expected Results (Success Case)

When everything works:

```json
{
  "results": {
    "student": {
      "register": { "user_id": "...", "email": "..." },
      "login": { "access_token": "...", "user_id": "..." },
      "getMe": { "email": "...", "role": "student" },
      "logout": { "message": "Logged out successfully" },
      "errors": []
    },
    "company": { ... },
    "admin": { ... }
  },
  "logs": {
    "errors": [],      // EMPTY - no errors
    "warnings": [],    // EMPTY - no warnings
    "console": [...]   // Just info logs
  }
}
```

---

## 🚨 Your Current Issue

Based on your description: "se va al fallback pero no alcanzo a guardar los logs"

**Diagnosis:** Logout is using the fallback mechanism, which means:
1. ✅ Frontend logout() function IS calling authManager.logout()
2. ✅ But authManager.logout() is failing
3. ✅ So it falls back to clearing localStorage manually
4. ✅ This works for localStorage, but logout() overall fails

**What to check:**
1. Is `/api/v1/auth/logout` returning an error?
2. Is the API_KEY being passed correctly?
3. Is there a network error?

**Use this test to find out!**

---

## 📞 Support

If tests show errors:

1. **Screenshot the errors** from the web interface
2. **Export the JSON report** - includes all details
3. **Share the report** - will show exactly what's failing

---

## 🔗 Related Files

- `app/core/auth.py` - Backend auth logic
- `app/api/endpoints/auth.py` - Auth endpoints
- `app/frontend/static/js/auth-manager.js` - Frontend auth manager
- `app/frontend/static/js/navbar-manager.js` - Global logout function

---

**Date**: 20 de noviembre de 2025  
**Version**: 1.0  
**Status**: ✅ Ready to use

