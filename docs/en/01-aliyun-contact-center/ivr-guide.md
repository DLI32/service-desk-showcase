# Alibaba Cloud Contact Center IVR Setup Guide

Sources: S1 and S2; see the [source table](../SOURCES.md). The specification describes the target; the retrospective describes the final implementation. Live testing covered the simplified Chinese flow, not the complete bilingual flow.

## Prerequisites

Use `<ALIYUN_ACCOUNT>` to provision the demo instance `<INSTANCE_ID>` and complete the service authorization required by the platform. Prepare four skill groups: new issues, status inquiries, password issues, and other issues. Each group must include agents who can go online. Manage inbound numbers and the allowlist only in the private console; this document uses `<TEST_NUMBER>` and `<PHONE>` throughout.

The historical trial environment imposed limits on a one-time allowlist, total calls, and instance recreation. The specification's statement that all slots had to be filled before submission was later corrected to guidance and an upper limit; it must not be treated as a mandatory submission condition. Confirm the rules in effect and the testers needed before provisioning.

## Minimal Chinese Flow: Four Routes Tested with Live Calls

```text
Start → Collect digits (greeting + menu) → Key branch
                               ├─ 1 → New issue → Transfer to agent → End
                               ├─ 2 → Status inquiry → Transfer to agent → End
                               ├─ 3 → Password issue → Transfer to agent → End
                               ├─ 4 → Other issue → Transfer to agent → End
                               └─ Other → Back to digit collection to listen again
```

The final model had 8 nodes and 25 connections. The greeting and menu were combined, duplicate transfer prompts were removed, and the transfer-to-agent node handled queue audio.

Original digit-collection prompt, translated:

> Welcome to the IT service desk. For a new issue, press 1. To check the status of an existing issue, press 2. For password issues, press 3. For other issues, press 4.

Historical configuration: a fixed single-digit input, two digit-collection loops, and a ten-second timeout. Transfers used assignment to the first available agent, with the built-in default queue music for all queues. Set priority, queue capacity, and timeouts according to the demo load; do not copy them as a production policy.

## Target Bilingual Prompts: Not Fully Deployed

First-level language selection:

> Welcome to the IT service desk. Thanks for calling IT Support. For Mandarin, press 1. For English, press 2.

Second-level Chinese menu, translated:

> For a new issue, press 1. To check the status of an existing issue, press 2. For password issues, press 3. For other issues, press 4.

Second-level English menu:

> For a new issue, press 1. To check the status of an existing issue, press 2. For password issues, press 3. For other issues, press 4.

Both languages route the four business options to the same skill groups. To extend the flow, add language digit collection and branching before the Chinese structure, then add the English nodes one route at a time.

| Purpose | Chinese Original, Translated | English Original |
|---|---|---|
| Invalid key | The key you pressed is invalid. Please select again. | Invalid option, please try again. |
| Transfer prompt | Transferring your call. Please hold. | Please hold while we transfer your call. |
| No agents available | All agents are currently busy. Please call again later. | All agents are busy. Please try again later. |

The specification recommended replaying once after a timeout, then transferring to other issues. In the final Chinese flow, the fallback branch returned to digit collection to replay the prompt. These must not be described as the same verified policy. Separate exits must also be designed for no agents available and outside business hours.

## Build Sequence

1. Build and publish the smallest viable structure, then add business branches. Resolve unexpected validation errors before continuing.
2. Create nodes one at a time and connect each output only once. Delete old connections before rewiring to avoid duplicate outputs.
3. Hover over a port, then drag all the way to the target input port. If a return connection is difficult to draw, temporarily move the target node, connect it, then move it back.
4. Save each section, check the success message, close and reopen the editor to verify outputs, then publish to validate. A line on the canvas does not prove that the saved model contains it.
5. After publishing successfully, bind the test number, reload the number management page, and read back the binding.
6. Set the agent workspace to online and place live calls from controlled, allowlisted devices.

In the historical minimal experiment, all four functional outputs of the transfer-to-agent node—success, failure, timeout, and queue overflow—had to be connected; caller hang-up and queue termination could remain empty. This was a tested finding in that environment, not a general platform requirement confirmed during this compilation.

## Troubleshooting and Acceptance

- Large flow fails to publish: start with a minimal flow that publishes and add incrementally. Avoid repeatedly redrawing connections in an unreliable model.
- Persistent error on the same node: check for duplicate outputs. One node's six outputs had once been duplicated into two sets.
- No save feedback: reopen the editor and confirm the save message and publication status. An old browser tab may silently stop working.
- Fewer nodes after cloning: cloning may retain only reachable nodes, so a clone cannot serve as a complete backup.
- Four-route acceptance: test each key, verify the skill group and actual agent connection, then record the time and result.

At the time, all four routes passed live-call tests. The invalid-key loop was checked only in the model, not with a live call; the complete four-route English flow was not delivered. The absence of a simulator that avoided dialing was an observation of the console at the time. Future testing should cover invalid keys, timeouts, no agents available, outside business hours, and hang-ups.
