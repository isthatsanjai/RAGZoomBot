document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded. Preparing to initialize Zoom SDK v3.13.2.");
    
    const joinButton = document.getElementById('join-btn');
    
    const logDiv = document.getElementById('log');

    if (typeof SharedArrayBuffer === 'undefined') {
        log('<strong>SharedArrayBuffer is not available. This may cause issues with the Zoom SDK.</strong>');
        log('Try using Chrome browser or enable SharedArrayBuffer in browser settings.');
    } else {
        log('SharedArrayBuffer is available.');
    }

    try {
        ZoomMtg.preLoadWasm();
        ZoomMtg.prepareWebSDK();
        log(' Zoom SDK prepared successfully.');
    } catch (error) {
        log(` <strong>Error preparing Zoom SDK:</strong> ${error.message}`);
        return;
    }

    function log(message) {
        console.log(message);
        const p = document.createElement('p');
        p.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
        logDiv.appendChild(p);
        logDiv.scrollTop = logDiv.scrollHeight;
    }



    joinButton.addEventListener('click', async () => {
        const meetingNumber = document.getElementById('meeting-number').value.replace(/\s+/g, '');
        const passWord = document.getElementById('meeting-password').value;
        const userName = document.getElementById('bot-name').value;
        
        if (!meetingNumber || !userName) { 
            alert('Please enter Meeting ID and Bot Name.'); 
            return; 
        }

        joinButton.disabled = true;
        joinButton.textContent = 'Joining...';

        log(` Requesting signature for meeting: ${meetingNumber}`);
        let signatureResponse;
        
        try {
            const response = await fetch('/api/generate-sdk-signature', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ meetingNumber, role: 0 })
            });
            
            if (!response.ok) throw new Error(`Signature request failed: ${response.statusText}`);
            signatureResponse = await response.json();
            log(` Signature generated successfully`);
        } catch (error) {
            log(` <strong>Error getting signature:</strong> ${error.message}`);
            joinButton.disabled = false;
            joinButton.textContent = ' Join Meeting as Bot';
            return;
        }

        if (!signatureResponse || !signatureResponse.signature) {
            log(' <strong>Could not join meeting: Signature was not generated.</strong>');
            joinButton.disabled = false;
            joinButton.textContent = ' Join Meeting as Bot';
            return;
        }

        log(`Initializing Zoom SDK...`);
        
        ZoomMtg.init({
            debug: false,
            leaveUrl: 'https://www.zoom.com',
            patchJsMedia: true,
            leaveOnPageUnload: true,
            success: () => {
                log('SDK Initialized successfully. Attempting to join meeting...');
                document.getElementById('zmmtg-root').style.display = 'block';
                ZoomMtg.join({
                    signature: signatureResponse.signature,
                    sdkKey: signatureResponse.apiKey,
                    meetingNumber: meetingNumber,
                    passWord: passWord,
                    userName: userName,
                    userEmail:'sanjaidini@gmail.com',
                    success: (success) => {
                        log('🎉 <strong>✅ Successfully joined meeting! Bot is now listening for chat messages...</strong>');
                        setupChatListener(meetingNumber, userName);
                        joinButton.textContent = '✅ Joined Meeting';
                        console.log(success);
                    },
                    error: (err) => {
                        log(` <strong>Error joining meeting:</strong>`);
                        log(`   Error Code: ${err.errorCode || 'Unknown'}`);
                        log(`   Error Message: ${err.errorMessage || JSON.stringify(err)}`);
                        
                        if (err.errorCode === 3712) {
                            log('    This usually means the meeting ID is invalid or the meeting has ended.');
                        } else if (err.errorCode === 3000) {
                            log('    This usually means invalid credentials or signature.');
                        }
                        
                        joinButton.disabled = false;
                        joinButton.textContent = ' Join Meeting as Bot';
                    }
                });
            },
            error: (err) => {
                log(` <strong>Error initializing SDK:</strong>`);
                log(`   Error: ${JSON.stringify(err)}`);
                joinButton.disabled = false;
                joinButton.textContent = ' Join Meeting as Bot';
            }
        });
    });

function setupChatListener(meetingId, botName) {
    log(`Setting up chat listener for meeting ${meetingId}...`);
    
    // Get list of existing participants and send welcome messages
    setTimeout(() => {
        ZoomMtg.getAttendeeslist({
            success: function(data) {
                // Log the full object for debugging, as seen in console.
                log(`Successfully retrieved participant list object: ${JSON.stringify(data)}`);
                
                // CORRECTED: The actual array is at data.result.attendeesList
                const attendees = data?.result?.attendeesList;

                if (attendees && attendees.length > 0) {
                    log(`Found ${attendees.length} existing participants.`);
                    
                    // Send welcome message to all existing participants (except the bot itself)
                    attendees.forEach(participant => {
                        if (participant.userName !== botName) {
                            const welcomeMessage = "Hi! I'm a chat bot, here to help with any questions you have about The Fitness Doctor.";
                            log(`Sending welcome DM to existing participant: ${participant.userName} (User ID: ${participant.userId})`);
                            
                            ZoomMtg.sendChat({
                                message: welcomeMessage,
                                userId: participant.userId
                            });
                        }
                    });
                } else {
                    log('Could not find any existing participants in the returned data.');
                }
            },
            error: function(error) {
                log(`❌ Error getting attendees list: ${JSON.stringify(error)}`);
            }
        });
    }, 3000); // Wait for 3 seconds before sending welcome messages
        
    ZoomMtg.inMeetingServiceListener('onReceiveChatMsg', (chatData) => {
        log(chatData);
        log(`Chat received from ${chatData.sender}: "${chatData?.content?.text}"`);
        
        if (chatData.sender === botName) { 
            return log('   ↳ Ignoring own message.'); 
        }
        
        processChatMessage(meetingId, chatData);
    });

    ZoomMtg.inMeetingServiceListener('onUserJoin', (data) => {
        log(`A new user joined: ${JSON.stringify(data)}`);

        // Check if the joined user is the bot itself
        if (data.userName !== botName) {
            
            const welcomeMessage = "Hi! I'm a chat bot, here to help with any questions you have about The Fitness Doctor.";
            
            log(`Preparing to send welcome DM to ${data.userName} (User ID: ${data.userId})`);

            // Wait for 2 seconds before sending the welcome message
            setTimeout(() => {
                log(`Sending welcome DM to ${data.userName}...`);
                ZoomMtg.sendChat({
                    message: welcomeMessage,
                    userId: data.userId  // Use the userId to send a Direct Message.
                });
            }, 2000); 

        } else {
            log('   ↳ The new user is the bot itself. Ignoring.');
        }
    });

    ZoomMtg.inMeetingServiceListener('onMeetingStatus', (data) => {
        log(`📊 Meeting status update: ${JSON.stringify(data)}`);
    });
}

    async function processChatMessage(meetingId, chatData) {
        log(`🤖 Processing chat message from ${chatData.sender}...`);
        
        try {
            const response = await fetch('/api/process-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    meeting_id: meetingId, 
                    message: chatData?.content?.text, 
                    user_name: chatData?.sender
                })
            });
            
            const data = await response.json();
            
            if (data && data.reply) {
                log(`💭 Backend provided a reply. Sending to ${chatData.senderName}...`);
                ZoomMtg.sendChat({ 
                    message: data.reply, 
                    userId: chatData.senderId
                });
                log(`✅ Reply sent: "${data.reply}"`);
            } else {
                log('   ↳ Backend determined no reply was needed.');
            }
        } catch (error) {
            log(`❌ <strong>Error processing chat message:</strong> ${error.message}`);
        }
    }
});