# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import smtplib
from email.message import EmailMessage
from uuid import uuid4

from nemoguardrails import LLMRails
from nemoguardrails.actions import action
from nemoguardrails.actions.actions import ActionResult
from nemoguardrails.kb.kb import KnowledgeBase
from nemoguardrails.llm.output_parsers import _replace_prefix

SENDER_EMAIL = "sender@example.com"
SMTP_SERVER = "localhost"
SMTP_PORT = 8025


@action()
async def RetrieveRelevantChunksAction(
    context: dict, kb: KnowledgeBase
) -> ActionResult:
    user_message = context.get("last_user_message")
    context_updates = {}

    # For our custom RAG, we re-use the built-in retrieval
    chunks = await kb.search_relevant_chunks(user_message)
    relevant_chunks = "\n".join([chunk["body"] for chunk in chunks])
    # Store the chunks for downstream use
    context_updates["relevant_chunks"] = relevant_chunks

    return ActionResult(return_value=relevant_chunks, context_updates=context_updates)


@action()
async def SendAuthenticationEmailAction(
    email_transcript: str, context: dict
) -> ActionResult:
    # TODO Add param check to ensure `email_transcript` contains a valid email address.

    name = context.get("name", "there")
    greeting = f"Hi {name if name else 'there'}!"
    token = str(uuid4())
    body = f"{greeting}\n\nPlease enter the code below into your open conversation:\n{token}"
    subject = "Login to Support Bot"

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = email_transcript

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(SENDER_EMAIL, email_transcript, msg.as_string())
        return ActionResult(return_value=token)
    except Exception as e:
        print(f"Failed to send email: {e}")
        return ActionResult(return_value="None")


def user_intent_parser(output: str) -> str:
    return _replace_prefix(output.strip().lower(), "user intent: ", "")


def init(app: LLMRails):
    # Actions
    app.register_action(RetrieveRelevantChunksAction, "RetrieveRelevantChunksAction")
    app.register_action(SendAuthenticationEmailAction, "SendAuthenticationEmailAction")

    # Output parsers
    app.register_output_parser(user_intent_parser, "my_user_intent")
