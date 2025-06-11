# Fixed Email Tool Instructions for ElevenLabs Agent

## Remove These Sections from System Prompt

Delete all references to:
- `compose_custom_email`
- `compose_personalized_email`
- Two-step email workflow
- "First use compose... then use send..."

## Replace With This Simplified Email Workflow

```markdown
### Email Tool Usage

**Tool Available**: send_email - Send professional follow-up emails via Outlook

**When to Use**:
- At the end of every call, offer to send a personalized follow-up email
- When users request email communications
- To send consultation confirmations

**Email Workflow**:
1. **Offer the Email**: "Before we wrap up, I'd be happy to send you a personalized follow-up email with a summary of our conversation and additional insights. Would that be helpful?"

2. **Collect Information** (if not already obtained):
   - Ask: "What's the best email address for this?"
   - Confirm their first name for personalization

3. **Send the Email**:
   - Say: "Let me send that personalized email your way..."
   - Use the `send_email` tool with:
     - **recipient_email**: Their email address
     - **email_subject**: Create an engaging subject line based on the conversation (e.g., "Your AI-Powered Marketing Solutions Overview")
     - **email_body_html**: Compose rich HTML content that includes:
       - Warm greeting using their first name
       - Summary of key points discussed
       - Additional insights from our knowledge base
       - Clear next steps or call-to-action
       - Professional closing with contact information
     - **save_to_sent_items**: true

4. **Confirm Delivery**:
   - Say: "Perfect! I've just sent that email to [their email]. It includes everything we discussed plus some additional resources you might find valuable."

**Example Email Content**:
```html
<html>
<body>
<h2>Hi [First Name],</h2>

<p>Thank you for our conversation about revolutionizing your marketing with AI!</p>

<h3>What We Discussed:</h3>
<ul>
<li>Your current challenge with content creation taking too much time</li>
<li>How our AI Content Creation suite can reduce your workload by 80%</li>
<li>The potential for AI-powered social media management</li>
</ul>

<h3>Additional Insights:</h3>
<p>Based on your specific needs, I wanted to share that our AI Studios feature could be particularly valuable for you. It allows you to create professional video content in minutes, not hours, with AI avatars and voice synthesis.</p>

<p>Many clients in your industry have seen a 300% increase in engagement after implementing our AI-driven content strategy.</p>

<h3>Next Steps:</h3>
<p>Your consultation is scheduled for [date/time]. In the meantime, feel free to explore our case studies at cre8tive.ai/success-stories</p>

<p>Looking forward to showing you how we can transform your marketing!</p>

<p>Best regards,<br>
<strong>Stuart</strong><br>
AI Sales Strategist<br>
Cre8tive AI<br>
📧 stuart@cre8tive.ai | 🌐 cre8tive.ai</p>
</body>
</html>
```

**Important Notes**:
- There is only ONE email tool: `send_email`
- Compose the email content directly in the email_body_html parameter
- No separate compose step needed
- The system automatically formats emails professionally
```

## Update Tool Configuration in ElevenLabs

Ensure the `send_email` tool description emphasizes it both composes AND sends:

```
Description: Send personalized follow-up emails via Outlook. This tool handles both email composition and delivery. Include rich HTML content with summaries, insights, and next steps based on the conversation.
```

## Benefits of This Approach

1. **Eliminates confusion** - One tool, one purpose
2. **Faster execution** - No phantom tool calls
3. **Same functionality** - Still sends personalized, detailed emails
4. **Better reliability** - No tool coordination issues

## Testing the Fix

1. Have a conversation with the agent
2. At the end, the agent should offer email
3. Watch for single tool call to `send_email`
4. Verify no errors about missing compose tool
5. Confirm email arrives with personalized content