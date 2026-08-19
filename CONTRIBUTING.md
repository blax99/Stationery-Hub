# Contributing to Stationery-Hub

This guide explains how each team member should set up the project, create a feature branch, run Django + Tailwind, develop their assigned module, and submit changes through a Pull Request.

## 1. Clone the Repository

```bash
git clone <REPOSITORY-URL>
cd Stationery-Hub
```

## 2. Switch to `dev`

Always start from the latest `dev` branch:

```bash
git checkout dev
git pull origin dev
```

> **Do not create your feature branch from `main`.**

## 3. Create Your Own Python Virtual Environment

Each team member must create their **own local Python virtual environment**.

```bash
python -m venv venv
```

This creates:

```text
Stationery-Hub/
└── venv/
```

The `venv` folder is local to your computer and **must not be committed or pushed to Git**.

### Activate the Virtual Environment

**Windows PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
venv\Scripts\activate
```

After activation, your terminal should show something similar to:

```text
(venv) PS C:\...\Stationery-Hub>
```

### Why does everyone need their own `venv`?

Each developer should have a separate local environment:

```text
Developer 1 → local venv
Developer 2 → local venv
Developer 3 → local venv
...
```

The repository does **not** contain the virtual environments. Instead, `requirements.txt` contains the Python dependencies so every developer can recreate the environment locally.

## 4. Install Python Packages

After activating the virtual environment:

```bash
pip install -r requirements.txt
```

If you install a new Python package during development, update `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Commit the updated `requirements.txt` so other team members can install the dependency.

## 5. Install Node.js Packages

Make sure Node.js and npm are installed:

```bash
node -v
npm -v
```

Then install the project's Node.js dependencies:

```bash
npm install
```

This uses:

* `package.json`
* `package-lock.json`

to install the required Node.js and Tailwind dependencies.

> **Do not commit `node_modules/`.** It should be included in `.gitignore`.

## 6. Project Setup

After completing the setup, your project should look approximately like this:

```text
Stationery-Hub/
│
├── venv/                 ← local, NOT committed
├── node_modules/         ← local, NOT committed
├── manage.py
├── requirements.txt
├── package.json
├── package-lock.json
└── ...
```

The following files should be committed:

```text
requirements.txt
package.json
package-lock.json
```

The following should normally **not** be committed:

```text
venv/
node_modules/
.env
```

## 7. Run Django and Tailwind

Django and Tailwind should run simultaneously, so use **two terminals**.

### Terminal 1 — Django

Activate the virtual environment:

```powershell
venv\Scripts\Activate.ps1
```

Then run Django:

```bash
python manage.py runserver
```

Keep this terminal running.

### Terminal 2 — Tailwind

Open another terminal in the project directory and run:

```bash
npm run dev
```

This starts the Tailwind development/watch process defined in `package.json`.

Keep this terminal running as well.

The development environment should therefore be:

```text
Terminal 1
└── Django
    └── python manage.py runserver

Terminal 2
└── Tailwind
    └── npm run dev
```

## 8. Create Your Feature Branch

Once your environment is ready, create a branch for your assigned module.

Examples:

```bash
git checkout -b feature/auth
```

```bash
git checkout -b feature/products
```

```bash
git checkout -b feature/cart
```

```bash
git checkout -b feature/orders
```

```bash
git checkout -b feature/payment
```

```bash
git checkout -b feature/admin
```

Feature branches must be created from the **latest `dev` branch**.

## 9. Work Only on Your Assigned Module

For example, if you are responsible for Authentication, your work might include:

```text
authentication/
├── models.py
├── views.py
├── serializers.py
├── urls.py
└── ...
```

Follow the project's existing architecture and conventions.

Avoid modifying another team member's module unnecessarily.

If your feature requires changes to another module, communicate with the responsible team member before making those changes.

## 10. Check Your Changes

Before committing:

```bash
git status
```

Review your changes:

```bash
git diff
```

Test your module and make sure both Django and Tailwind are running correctly.

Fix errors before pushing your code.

## 11. Commit Your Changes

Stage your changes:

```bash
git add .
```

Create a meaningful commit:

```bash
git commit -m "feat: Add user authentication"
```

Examples:

```text
feat: Add user registration
feat: Add product filtering
fix: Resolve authentication validation error
fix: Correct cart quantity update
```

Avoid vague commit messages such as:

```text
changes
final
done
test
```

## 12. Push Your Feature Branch

For the first push:

```bash
git push -u origin feature/auth
```

Replace `feature/auth` with your own branch name.

After the first push:

```bash
git push
```

## 13. Create a Pull Request

Go to GitHub and create a Pull Request.

For normal feature development, use:

```text
base:    dev
compare: feature/auth
```

Do **not** normally create feature Pull Requests directly into `main`.

The normal development flow is:

```text
feature/auth → dev
```

## 14. Code Review

Pull Requests should be reviewed before merging.

The review process may include:

* GitHub Copilot review, if enabled
* Human team-member review
* Testing of the submitted feature

If changes are requested, make the changes locally:

```bash
git add .
git commit -m "fix: Address authentication review comments"
git push
```

The existing Pull Request will automatically update.

You do **not** need to create another Pull Request.

## 15. After Your Feature Is Merged

Once your feature branch has been merged into `dev`, synchronize your local `dev` branch:

```bash
git checkout dev
git pull origin dev
```

For your next task, create a new feature branch:

```bash
git checkout -b feature/auth-login
```

Do not continue adding unrelated work to an already-merged feature branch.

## Complete Workflow

```text
Clone Repository
      ↓
Checkout dev
      ↓
Pull latest dev
      ↓
Create local venv
      ↓
pip install -r requirements.txt
      ↓
npm install
      ↓
Start Django + Tailwind
      ↓
Create feature branch
      ↓
Work on assigned module
      ↓
Test changes
      ↓
Commit changes
      ↓
Push feature branch
      ↓
Create Pull Request
      ↓
Code Review
      ↓
Merge feature → dev
      ↓
Pull latest dev
      ↓
Start next feature
```

## Important Team Rules

1. **Never push directly to `main`.**
2. **Do not normally push directly to `dev`.**
3. Always create feature branches from the latest `dev`.
4. Every developer must use their **own local `venv`**.
5. Never commit `venv/`.
6. Never commit `node_modules/`.
7. Never commit `.env` files or secrets.
8. Update and commit `requirements.txt` when Python dependencies change.
9. Commit `package.json` and `package-lock.json` when Node.js dependencies change.
10. Do not modify another member's module without communicating first.
11. Test your changes before creating a Pull Request.
12. Normal feature Pull Requests should target **`dev`**.
13. `dev` should be merged into `main` when the project is considered stable/release-ready.
14. If `dev` changes while you are working, synchronize your branch with the latest `dev` before the Pull Request is merged to reduce merge conflicts.

## Quick Setup for a New Team Member

```bash
git clone <REPOSITORY-URL>
cd Stationery-Hub

git checkout dev
git pull origin dev

python -m venv venv
venv\Scripts\Activate.ps1

pip install -r requirements.txt
npm install

git checkout -b feature/<your-module>
```

Then use two terminals:

**Terminal 1:**

```bash
python manage.py runserver
```

**Terminal 2:**

```bash
npm run dev
```

When your work is complete:

```bash
git add .
git commit -m "Describe your changes"
git push -u origin feature/<your-module>
```

Then create the Pull Request:

```text
feature/<your-module> → dev
```

> **Before starting a new feature, always return to `dev` and pull the latest changes first.** This is one of the simplest ways to reduce merge conflicts in a team project.
