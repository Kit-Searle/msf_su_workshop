# Setup Instructions for MSF Project

Follow these steps to set up and run the workbook.

---

## Prerequisites
Before you begin, make sure you have the following installed:
- [Anaconda](https://www.anaconda.com/download)
- Git (optional, if you plan to clone the repository)

---

### Step 1: Open Anaconda Prompt
Launch **Anaconda Prompt** from your Start Menu.

---

### Step 2: Create a New Environment
Run the following command to create a new environment with Python 3.12.10:

```bash
conda create -n msf_workshop python=3.12.11
```

---

### Step 3: Activate the Environment
Activate the environment with:

```bash
conda activate msf_workshop
```

---

### Step 4: Navigate to the Project Folder
Use `cd` to change into the project directory.  
For example:

```bash
cd "C:\Users\username\msf_workshop"
```

---

### Step 5: Install Dependencies
Install the required packages:

```bash
pip install -r requirements.txt
```
---

✅ Your environment is now fully set up!
You can open jupyter notebook and open the file `msf_workshop.ipynb`.

```bash
jupyter notebook
```