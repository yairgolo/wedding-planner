(() => {
  const config = window.portalConfig;
  if (!config) return;
  const dialog = document.querySelector("#sendDialog");
  const preview = document.querySelector("#messagePreview");
  const title = document.querySelector("#dialogName");
  const share = document.querySelector("#shareButton");
  const confirmArea = document.querySelector("#confirmArea");
  let activeId = null, activeData = null, imageFile = null;
  const endpoint = (template, id) => template.replace(/\/0(?=\/|$)/, `/${id}`);
  const request = (url, body) => fetch(url, {method:"POST", credentials:"same-origin", headers:{"Content-Type":"application/x-www-form-urlencoded","Accept":"application/json"}, body:new URLSearchParams({...body, csrf_token:config.csrf})}).then(async r=>{const data=await r.json();if(!r.ok)throw new Error(data.error||"הפעולה נכשלה");return data});
  async function fileFromImage(url){const res=await fetch(url,{credentials:"same-origin"});if(!res.ok)throw new Error("תמונת ההזמנה אינה זמינה");const blob=await res.blob();return new File([blob],"wedding-invitation.jpg",{type:blob.type||"image/jpeg"})}
  document.querySelectorAll(".send-button").forEach(button=>button.addEventListener("click",async()=>{try{activeId=button.dataset.guest;button.disabled=true;const data=await request(endpoint(config.prepareUrl,activeId),{});if(!data.image_url)throw new Error("המנהל עדיין לא העלה תמונת הזמנה.");activeData=data;imageFile=await fileFromImage(data.image_url);title.textContent=button.closest(".guest").querySelector("strong").textContent;preview.textContent=data.text;confirmArea.hidden=true;share.hidden=false;dialog.showModal()}catch(error){alert(error.message)}finally{button.disabled=false}}));
  document.querySelector("[data-close]").addEventListener("click",()=>dialog.close());
  share.addEventListener("click",async()=>{try{if(!navigator.share)throw new Error("המכשיר אינו תומך בשיתוף. נסה/י בדפדפן הטלפון.");if(navigator.canShare&&!navigator.canShare({files:[imageFile]}))throw new Error("המכשיר אינו מאפשר צירוף תמונה.");await navigator.share({files:[imageFile],title:"הזמנה",text:activeData.text});share.hidden=true;confirmArea.hidden=false}catch(error){if(error.name!=="AbortError")alert(error.message)}});
  document.querySelectorAll("[data-confirm]").forEach(button=>button.addEventListener("click",async()=>{try{await request(endpoint(config.confirmUrl,activeId),{sent:button.dataset.confirm});window.location.reload()}catch(error){alert(error.message)}}));
})();
