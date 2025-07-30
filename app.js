require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const db = require('./db');

const { GoogleGenerativeAI } = require('@google/generative-ai');
const gemini = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const app = express();
const port = process.env.PORT || 5000;

const WHATSAPP_API_TOKEN = process.env.WHATSAPP_API_TOKEN;
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
const VERIFY_TOKEN = process.env.VERIFY_TOKEN;
const WHATSAPP_GRAPH_API_URL = `https://graph.facebook.com/v19.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`;

app.use(bodyParser.json());
app.use('/images', express.static('images'));

const userStates = {};

// Fallback AI assistant
async function askGemini(prompt) {
  try {
    const model = gemini.getGenerativeModel({ model: 'gemini-pro' });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (err) {
    console.error('Gemini error:', err);
    return "🤖 Sorry, I couldn't answer that right now. Please try again later.";
  }
}

// Generic send
async function sendWhatsAppMessage(to, payload) {
  try {
    await axios.post(
      WHATSAPP_GRAPH_API_URL,
      { messaging_product: 'whatsapp', to, ...payload },
      { headers: { Authorization: `Bearer ${WHATSAPP_API_TOKEN}` } }
    );
  } catch (err) {
    console.error('WhatsApp send error:', err.response?.data || err.message);
  }
}

// Helpers
const sendText = (to, text) => sendWhatsAppMessage(to, { type: 'text', text: { body: text } });
const sendList = (to, header, body, options, btnText = 'Select') => sendWhatsAppMessage(to, {
  type: 'interactive', interactive: {
    type: 'list', header: { type: 'text', text: header }, body: { text: body },
    action: { button: btnText, sections: [{ title: 'Options', rows: options }] }
  }
});

// Budget step
async function sendBudgetList(to) {
  const opts = [
    { id: 'budget_under_5', title: 'Under 5 Lakhs' },
    { id: 'budget_5_10', title: '5-10 Lakhs' },
    { id: 'budget_10_20', title: '10-20 Lakhs' },
    { id: 'budget_20_above', title: '20 Lakhs & Above' }
  ];
  await sendList(to, 'Select Budget', 'Choose your budget range:', opts);
}

// Type step
async function sendTypeList(to, budgetId) {
  let clause;
  if (budgetId === 'budget_under_5') clause = '"estimated_selling_price" < 500000';
  else if (budgetId === 'budget_5_10') clause = '"estimated_selling_price" BETWEEN 500000 AND 1000000';
  else if (budgetId === 'budget_10_20') clause = '"estimated_selling_price" BETWEEN 1000000 AND 2000000';
  else clause = '"estimated_selling_price" > 2000000';

  try {
    const res = await db.query(`SELECT DISTINCT type FROM cars WHERE ${clause}`);
    console.log('Type options:', res.rows);
    const opts = res.rows.map(r => ({ id: r.type, title: r.type }));
    if (opts.length) await sendList(to, 'Select Type', 'Choose car type:', opts);
    else await sendText(to, 'No types available for this budget.');
  } catch (e) {
    console.error('Type fetch error:', e);
    await sendText(to, 'Error fetching car types.');
  }
}

// Brand step
async function sendBrandList(to, budgetId, type) {
  let clause;
  if (budgetId === 'budget_under_5') clause = '"estimated_selling_price" < 500000';
  else if (budgetId === 'budget_5_10') clause = '"estimated_selling_price" BETWEEN 500000 AND 1000000';
  else if (budgetId === 'budget_10_20') clause = '"estimated_selling_price" BETWEEN 1000000 AND 2000000';
  else clause = '"estimated_selling_price" > 2000000';

  try {
    const res = await db.query(
      `SELECT DISTINCT make FROM cars WHERE ${clause} AND LOWER(type)=LOWER($1)`,
      [type]
    );
    const opts = res.rows.map(r => ({ id: r.make, title: r.make }));
    if (opts.length) await sendList(to, 'Select Brand', 'Choose car brand:', opts);
    else await sendText(to, 'No brands for this type & budget.');
  } catch (e) {
    console.error('Brand fetch error:', e);
    await sendText(to, 'Error fetching brands.');
  }
}

// Car listing
async function sendCarList(to, budgetId, type, brand, offset = 0) {
  let priceClause;
  if (budgetId === 'budget_under_5') priceClause = `"estimated_selling_price" < 500000`;
  else if (budgetId === 'budget_5_10') priceClause = `"estimated_selling_price" BETWEEN 500000 AND 1000000`;
  else if (budgetId === 'budget_10_20') priceClause = `"estimated_selling_price" BETWEEN 1000000 AND 2000000`;
  else priceClause = `"estimated_selling_price" > 2000000`;

  try {
    const cars = await db.query(
      `SELECT make, model, variant, manufacturing_year, fuel_type, estimated_selling_price
       FROM cars
       WHERE ${priceClause}
         AND LOWER(type)=LOWER($1)
         AND LOWER(make)=LOWER($2)
       ORDER BY estimated_selling_price ASC
       LIMIT 5 OFFSET $3`,
      [type, brand, offset]
    );

    if (!cars.rows.length) {
      await sendText(to, offset === 0 ? 'No cars found.' : 'No more cars.');
      return;
    }

    for (const c of cars.rows) {
      const file = `${c.make}_${c.model}_${c.variant}`.replace(/\s+/g, '_') + '.png';
      const url = `${process.env.NGROK_URL}/images/${file}`;
      const caption =
        `🚗 ${c.make} ${c.model} ${c.variant}\n` +
        `📅 Year: ${c.manufacturing_year}\n` +
        `⛽ Fuel: ${c.fuel_type}\n` +
        `💰 Price: ₹${c.estimated_selling_price}`;

      let sentImage = false;
      try {
        await sendWhatsAppMessage(to, {
          type: 'image',
          image: { link: url, caption }
        });
        sentImage = true;
      } catch (err) {
        console.warn(`Image send failed for ${file}, showing text only.`, err.message);
        await sendText(to, caption);
      }

      // Send select button
      const id = `book_${c.make}_${c.model}_${c.variant}`.replace(/\s+/g, '_');
      await sendWhatsAppMessage(to, {
        type: 'interactive',
        interactive: {
          type: 'button',
          body: { text: 'SELECT' },
          action: {
            buttons: [
              {
                type: 'reply',
                reply: {
                  id,
                  title: 'SELECT'
                }
              }
            ]
          }
        }
      });

      await new Promise(r => setTimeout(r, 500));
    }

    // Handle pagination
    if (cars.rows.length === 5) {
      userStates[to].offset = offset + 5;
      userStates[to].step = 'VIEW_CARS';
      await sendText(to, 'Type "more" for more cars.');
    } else {
      userStates[to].step = 'DONE_VIEWING';
    }

  } catch (e) {
    console.error('Car fetch error:', e);
    await sendText(to, 'Error fetching cars.');
  }
}

async function sendTimeSlotButtons(to) {
  await sendWhatsAppMessage(to, {
    type:'interactive', interactive:{
      type:'button', body:{ text:'Which time works for you?' },
      action:{ buttons:[
        {type:'reply',reply:{id:'slot_morning',title:'Morning'}},
        {type:'reply',reply:{id:'slot_afternoon',title:'Afternoon'}},
        {type:'reply',reply:{id:'slot_evening',title:'Evening'}}
      ]}
    }
  });
}

// Webhook POST
app.post('/webhook', async (req, res) => {
  const msg = req.body.entry?.[0]?.changes?.[0]?.value?.messages?.[0];
  if (!msg) return res.sendStatus(200);
  const from = msg.from;
  userStates[from] = userStates[from]||{};
  const st = userStates[from];

  if (msg.type==='text') {
    const t = msg.text.body.trim().toLowerCase();
    if (['hi','hello','start'].includes(t)) {
      st.step='GREETING';
      await sendWhatsAppMessage(from, { type:'interactive', interactive:{ type:'button', body:{ text:'Hello! 👋 Welcome to “Sherpa Hyundai”. Im here to help you find your perfect used car. How can I assist you today?' }, action:{ buttons:[{type:'reply',reply:{id:'browse_used_cars',title:'Browse Cars'}}]}}});
    } else if (t==='more' && st.step==='VIEW_CARS') {
      await sendCarList(from, st.budget, st.type, st.brand, st.offset);
    } else if (st.step==='ASK_NAME') {
      st.name=msg.text.body.trim(); st.step='ASK_PHONE';
      await sendText(from,'Please enter your contact phone number.');
    } else if (st.step==='ASK_PHONE') {
      st.phone=msg.text.body.trim(); st.step='ASK_DL';
      await sendWhatsAppMessage(from,{type:'interactive',interactive:{type:'button',body:{text:'Do you have a valid driving license?'},action:{buttons:[{type:'reply',reply:{id:'dl_yes',title:'Yes'}},{type:'reply',reply:{id:'dl_no',title:'No'}}]}}});
    } else if (st.step==='CONFIRM_DETAILS') {
      // handled in interactive
    } else {
      const reply=await askGemini(msg.text.body.trim());
      await sendText(from,reply);
    }
  } else if (msg.type==='interactive') {
    const sel=msg.interactive.list_reply?.id||msg.interactive.button_reply?.id;

    if (sel==='browse_used_cars') {
      st.step='ASK_BUDGET'; 
      await sendText(from, "Great choice! What's your budget range?");
      await sendBudgetList(from);
    } else if (st.step==='ASK_BUDGET') {
      st.budget=sel; st.step='ASK_TYPE';
      await sendText(from, "Perfect! What type of car do you prefer?");
      await sendTypeList(from,sel);
    } else if (st.step==='ASK_TYPE') {
      st.type=sel; st.step='ASK_BRAND'; 
      await sendText(from, "Excellent choice!. Which brand do you prefer?");
      await sendBrandList(from,st.budget,st.type);
    } else if (st.step==='ASK_BRAND') {
      st.brand=sel; st.offset=0;
      await sendText(from, "Excellent choice!Here are some cars that match your criteria:");
      await sendCarList(from,st.budget,st.type,st.brand,0);
    } else if (sel.startsWith('book_')) {
      st.selectedCar=sel.replace('book_','').split('_').join(' ');
      st.step='SELECT_DATE';
      await sendList(from,'Schedule Test Drive',`When for your ${st.selectedCar}?`,[
        {id:'testdrive_today',title:'Today'},{id:'testdrive_tomorrow',title:'Tomorrow'},{id:'testdrive_later_this_week',title:'Later This Week'},{id:'testdrive_next_week',title:'Next Week'}
      ],'Choose');
    } else if (['testdrive_today','testdrive_tomorrow','testdrive_later_this_week','testdrive_next_week'].includes(sel)) {
      const map={testdrive_today:'Today',testdrive_tomorrow:'Tomorrow',testdrive_later_this_week:'Later This Week',testdrive_next_week:'Next Week'};
      st.dateChoice=map[sel]; st.step='SELECT_TIME_SLOT'; await sendTimeSlotButtons(from);
    } else if (['slot_morning','slot_afternoon','slot_evening'].includes(sel)) {
      const hours={slot_morning:9,slot_afternoon:14,slot_evening:18};
      const offs={Today:0,Tomorrow:1,'Later This Week':3,'Next Week':7};
      const dt=new Date(); dt.setDate(dt.getDate()+offs[st.dateChoice]); dt.setHours(hours[sel],0,0,0);
      st.datetime=dt; st.step='ASK_NAME'; await sendText(from,`Great—${st.dateChoice} at ${hours[sel]}:00! Your name?`);
    } else if (['dl_yes','dl_no'].includes(sel)) {
  // Store DL answer
  st.hasDL = sel === 'dl_yes';
  st.step = 'CONFIRM_DETAILS';

  // 1) Build the summary text
  const dt = st.datetime;
  const dateStr = dt.toLocaleDateString('en-IN', { weekday:'long', month:'short', day:'numeric' });
  const timeStr = dt.toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' });
  const summary =
    `📝 *Test Drive Summary:*\n` +
    `🚗 Car: ${st.selectedCar}\n` +
    `📅 Date: ${dateStr}\n` +
    `⏰ Time: ${timeStr}\n` +
    `🙋 Name: ${st.name}\n` +
    `📞 Phone: ${st.phone}\n` +
    `🪪 License: ${st.hasDL ? 'Yes' : 'No'}\n\n` +
    `Please confirm or cancel your test drive below:`;

  // 2) Send the summary as text
  await sendText(from, summary);

  // 3) Now show Confirm / Cancel buttons
  await sendWhatsAppMessage(from, {
    type: 'interactive',
    interactive: {
      type: 'button',
      body: { text: 'Choose an option:' },
      action: {
        buttons: [
          { type: 'reply', reply: { id: 'confirm_booking', title: 'Confirm' } },
          { type: 'reply', reply: { id: 'cancel_booking',  title: 'Cancel'  } }
        ]
      }
    }
  });
}


    } else if (sel==='confirm_booking') {
       await db.query(
    `INSERT INTO test_drives (user_id, car, datetime, name, phone, has_dl)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [from, userState[from].selectedCar, userState[from].datetime, userState[from].name, userState[from].phone, userState[from].hasDL]
  );
  await sendText(from, "✅ Your test drive is confirmed! Thank you. We'll contact you soon.");
  delete userStatus[from];
  delete userState[from];
}
    else if (sel==='cancel_booking') {
      await sendText(from,'❌ Booking canceled.'); userStates[from]={};
    }
  
  res.sendStatus(200);
});

// Verification
app.get('/webhook',(req,res)=>{
  const mode=req.query['hub.mode'],token=req.query['hub.verify_token'],challenge=req.query['hub.challenge'];
  if(mode==='subscribe'&&token===VERIFY_TOKEN) res.status(200).send(challenge);
  else res.sendStatus(403);
});

app.listen(port,()=>console.log(`Bot on port ${port}`));
