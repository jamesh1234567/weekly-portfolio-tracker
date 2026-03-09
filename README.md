# Weekly Portfolio Tracker
   
   Sends weekly email updates about my stock portfolio.
   
   ## Features
   - Tracks stocks in multiple currencies
   - Converts everything to EUR
   - Weekly email every Sunday
```
6. Save and close

**Your folder should now look like:**
```
weekly-portfolio-tracker/
├── .github/
│   └── workflows/
│       └── weekly-update.yml
├── weekly_portfolio_tracker.py
├── portfolio.json
├── portfolio.json.example
├── requirements.txt
├── .gitignore
└── README.md
```

---

### PHASE 2: Test Locally

**Step 10: Install Python packages**

1. Press Windows key
2. Type: `cmd`
3. Press Enter (opens Command Prompt)
4. Navigate to your folder:
```
   cd C:\Users\YourName\Documents\weekly-portfolio-tracker
```
   (Replace with your actual path - or drag the folder into cmd to paste the path)
5. Install packages:
```
   pip install -r requirements.txt
```
6. Wait for it to finish

**Step 11: Set your email info**

Still in Command Prompt, type these (replace with your actual values):
```
set EMAIL_FROM=your-email@gmail.com
set EMAIL_TO=your-email@gmail.com
set EMAIL_PASSWORD=abcd efgh ijkl mnop
```
(Use the 16-character app password you created earlier)

**Step 12: Run the script**
```
python weekly_portfolio_tracker.py
```

**What should happen:**
- It prints "Fetching prices..."
- Shows each stock ticker
- Prints "Total Value: €XXX"
- Says "Email sent!"
- **Check your email** - you should have received it!

**If it works:** Great! Move to Phase 3.

**If it doesn't work:** Tell me the error message.

---

### PHASE 3: Upload to GitHub

**Step 13: Install Git** (if you don't have it)

1. Go to: https://git-scm.com/downloads
2. Download for Windows
3. Run the installer
4. Click "Next" on everything (defaults are fine)
5. **Close Command Prompt and open a NEW one** (important!)

**Step 14: Initialize Git in your folder**

Open Command Prompt, navigate to your folder again:
```
cd C:\Users\YourName\Documents\weekly-portfolio-tracker
```

Then type:
```
git init
```

You should see: `Initialized empty Git repository`

**Step 15: Add files to Git**
```
git add .
```

**Step 16: Commit files**
```
git commit -m "Initial commit"
```

**If it asks for your name:**
```
git config --global user.email "your-email@gmail.com"
git config --global user.name "Your Name"
```
Then try the commit again.

**Step 17: Create GitHub repository**

1. Go to: https://github.com
2. Log in (or create account if you don't have one)
3. Click the green "New" button (top left)
4. Repository name: `weekly-portfolio-tracker`
5. Description: "Weekly email updates for my portfolio"
6. Choose **Private** (your code stays private) or **Public** (anyone can see the code, but NOT your portfolio data)
7. **Do NOT** check any boxes (no README, no .gitignore, no license)
8. Click "Create repository"

**Step 18: Connect your local folder to GitHub**

GitHub will show you commands. Copy the ones under "...or push an existing repository from the command line"

They look like:
```
git remote add origin https://github.com/yourusername/weekly-portfolio-tracker.git
git branch -M main
git push -u origin main
```

Paste them into Command Prompt and press Enter.

**It might ask for your GitHub username and password** - enter them.

**Step 19: Verify upload**

1. Go back to GitHub in your browser
2. Refresh the page
3. You should see all your files!
4. **Check:** Make sure `portfolio.json` is NOT there (it should be ignored)
5. **Check:** Make sure `portfolio.json.example` IS there

---

### PHASE 4: Set Up GitHub Secrets

**Step 20: Add your email info to GitHub**

1. On your GitHub repository page
2. Click "Settings" (top right)
3. In left sidebar: "Secrets and variables" → "Actions"
4. Click "New repository secret"

**Add these 4 secrets:**

**Secret 1:**
- Name: `EMAIL_FROM`
- Value: `your-email@gmail.com`
- Click "Add secret"

**Secret 2:**
- Name: `EMAIL_TO`
- Value: `your-email@gmail.com`
- Click "Add secret"

**Secret 3:**
- Name: `EMAIL_PASSWORD`
- Value: `abcd efgh ijkl mnop` (your 16-character app password)
- Click "Add secret"

**Secret 4:** (This one is tricky)
- Name: `PORTFOLIO_DATA`
- Value: Your portfolio as ONE LINE of JSON with NO spaces:
```
  {"AAPL":{"shares":10,"buy_price":150.00,"currency":"USD"},"MSFT":{"shares":5,"buy_price":300.00,"currency":"USD"}}