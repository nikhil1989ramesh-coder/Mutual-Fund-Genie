# Fix production (one-time Vercel setting)

**I can’t access your Vercel account.** Only you can change project settings in the Vercel dashboard. Follow these steps once to fix https://nikhil-ramesh-ai-mfgenie.vercel.app:

1. **Open Vercel**  
   Go to [vercel.com/dashboard](https://vercel.com/dashboard) and log in.

2. **Open the right project**  
   Click the project that serves **nikhil-ramesh-ai-mfgenie.vercel.app** (the name may be similar, e.g. `nikhil-ramesh-ai-mfgenie` or `mutual-fund-genie`).

3. **Set Root Directory**  
   - Go to **Settings** (top tab).  
   - Under **General**, find **Root Directory**.  
   - Click **Edit**, enter **`frontend`** (no slash), click **Save**.

4. **Redeploy**  
   - Go to **Deployments**.  
   - Open the **⋯** menu on the latest deployment.  
   - Click **Redeploy**.  
   - (Optional) Turn **off** “Use existing Build Cache” for this redeploy, then confirm.

5. **Verify**  
   After the deploy finishes, open:
   - https://nikhil-ramesh-ai-mfgenie.vercel.app/api/faq  
   You should get JSON (not 404). Then try the main app URL and send a chat message.

No code changes are required; this is a dashboard-only setting.
