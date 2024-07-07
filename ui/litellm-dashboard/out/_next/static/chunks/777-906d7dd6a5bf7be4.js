"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[777],{777:function(e,t,o){o.d(t,{AZ:function(){return _},Au:function(){return X},BL:function(){return eo},Br:function(){return k},Dj:function(){return el},E9:function(){return ea},EY:function(){return ei},FC:function(){return S},Gh:function(){return Q},HK:function(){return Z},I1:function(){return u},J$:function(){return B},K_:function(){return es},N8:function(){return C},NV:function(){return i},Nc:function(){return H},O3:function(){return et},OU:function(){return J},Og:function(){return s},Ov:function(){return p},Qy:function(){return m},RQ:function(){return d},Rg:function(){return P},So:function(){return b},W_:function(){return g},X:function(){return z},XO:function(){return h},Xd:function(){return D},Xm:function(){return f},YU:function(){return er},Zr:function(){return l},ao:function(){return ec},b1:function(){return G},cu:function(){return Y},e2:function(){return q},fP:function(){return A},hT:function(){return L},hy:function(){return c},j2:function(){return O},jA:function(){return en},jE:function(){return ee},kK:function(){return n},kn:function(){return F},lg:function(){return K},mR:function(){return x},m_:function(){return T},n$:function(){return U},o6:function(){return N},pf:function(){return $},qm:function(){return a},rs:function(){return y},tN:function(){return v},um:function(){return W},v9:function(){return M},wX:function(){return w},wd:function(){return R},xA:function(){return V},zg:function(){return I}});var r=o(80588);let a=async e=>{try{let t=await fetch("/get/litellm_model_cost_map",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}}),o=await t.json();return console.log("received litellm model cost data: ".concat(o)),o}catch(e){throw console.error("Failed to get model cost map:",e),e}},n=async(e,t)=>{try{let o=await fetch("/model/new",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),r.ZP.success("Model created successfully. Wait 60s and refresh on 'All Models' page"),a}catch(e){throw console.error("Failed to create key:",e),e}},c=async e=>{try{let t=await fetch("/model/settings",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}},s=async(e,t)=>{console.log("model_id in model delete call: ".concat(t));try{let o=await fetch("/model/delete",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({id:t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),r.ZP.success("Model deleted successfully. Restart server to see this."),a}catch(e){throw console.error("Failed to create key:",e),e}},i=async(e,t)=>{if(console.log("budget_id in budget delete call: ".concat(t)),null!=e)try{let o=await fetch("/budget/delete",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({id:t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},l=async(e,t)=>{try{console.log("Form Values in budgetCreateCall:",t),console.log("Form Values after check:",t);let o=await fetch("/budget/new",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},h=async(e,t)=>{try{let o=await fetch("/invitation/new",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({user_id:t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},d=async e=>{try{let t=await fetch("/alerting/settings",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}},w=async(e,t,o)=>{try{if(console.log("Form Values in keyCreateCall:",o),o.description&&(o.metadata||(o.metadata={}),o.metadata.description=o.description,delete o.description,o.metadata=JSON.stringify(o.metadata)),o.metadata){console.log("formValues.metadata:",o.metadata);try{o.metadata=JSON.parse(o.metadata)}catch(e){throw r.ZP.error("Failed to parse metadata: "+e,10),Error("Failed to parse metadata: "+e)}}console.log("Form Values after check:",o);let a=await fetch("/key/generate",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({user_id:t,...o})});if(!a.ok){let e=await a.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let n=await a.json();return console.log("API Response:",n),n}catch(e){throw console.error("Failed to create key:",e),e}},p=async(e,t,o)=>{try{if(console.log("Form Values in keyCreateCall:",o),o.description&&(o.metadata||(o.metadata={}),o.metadata.description=o.description,delete o.description,o.metadata=JSON.stringify(o.metadata)),o.metadata){console.log("formValues.metadata:",o.metadata);try{o.metadata=JSON.parse(o.metadata)}catch(e){throw r.ZP.error("Failed to parse metadata: "+e,10),Error("Failed to parse metadata: "+e)}}console.log("Form Values after check:",o);let a=await fetch("/user/new",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({user_id:t,...o})});if(!a.ok){let e=await a.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let n=await a.json();return console.log("API Response:",n),n}catch(e){throw console.error("Failed to create key:",e),e}},u=async(e,t)=>{try{console.log("in keyDeleteCall:",t);let o=await fetch("/key/delete",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({keys:[t]})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to delete key: "+e,10),Error("Network response was not ok")}let a=await o.json();return console.log(a),a}catch(e){throw console.error("Failed to create key:",e),e}},y=async(e,t)=>{try{console.log("in teamDeleteCall:",t);let o=await fetch("/team/delete",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({team_ids:[t]})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to delete team: "+e,10),Error("Network response was not ok")}let a=await o.json();return console.log(a),a}catch(e){throw console.error("Failed to delete key:",e),e}},k=async function(e,t,o){let a=arguments.length>3&&void 0!==arguments[3]&&arguments[3],n=arguments.length>4?arguments[4]:void 0,c=arguments.length>5?arguments[5]:void 0;try{let s="/user/info";"App Owner"==o&&t&&(s="".concat(s,"?user_id=").concat(t)),"App User"==o&&t&&(s="".concat(s,"?user_id=").concat(t)),("Internal User"==o||"Internal Viewer"==o)&&t&&(s="".concat(s,"?user_id=").concat(t)),console.log("in userInfoCall viewAll=",a),a&&c&&null!=n&&void 0!=n&&(s="".concat(s,"?view_all=true&page=").concat(n,"&page_size=").concat(c));let i=await fetch(s,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!i.ok){let e=await i.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let l=await i.json();return console.log("API Response:",l),l}catch(e){throw console.error("Failed to create key:",e),e}},f=async(e,t)=>{try{let o="/team/info";t&&(o="".concat(o,"?team_id=").concat(t)),console.log("in teamInfoCall");let a=await fetch(o,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!a.ok){let e=await a.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let n=await a.json();return console.log("API Response:",n),n}catch(e){throw console.error("Failed to create key:",e),e}},m=async e=>{try{let t=await fetch("/global/spend",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to create key:",e),e}},g=async e=>{try{let t="/onboarding/get_token";t+="?invite_link=".concat(e);let o=await fetch(t,{method:"GET",headers:{"Content-Type":"application/json"}});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await o.json()}catch(e){throw console.error("Failed to create key:",e),e}},T=async(e,t,o,a)=>{try{let n=await fetch("/onboarding/claim_token",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({invitation_link:t,user_id:o,password:a})});if(!n.ok){let e=await n.text();throw r.ZP.error("Failed to delete team: "+e,10),Error("Network response was not ok")}let c=await n.json();return console.log(c),c}catch(e){throw console.error("Failed to delete key:",e),e}},j=!1,E=null,_=async(e,t,o)=>{try{let t=await fetch("/v2/model/info",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw e+="error shown=".concat(j),j||(e.includes("No model list passed")&&(e="No Models Exist. Click Add Model to get started."),r.ZP.info(e,10),j=!0,E&&clearTimeout(E),E=setTimeout(()=>{j=!1},1e4)),Error("Network response was not ok")}let o=await t.json();return console.log("modelInfoCall:",o),o}catch(e){throw console.error("Failed to create key:",e),e}},F=async e=>{try{let t=await fetch("/model_group/info",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok)throw await t.text(),Error("Network response was not ok");let o=await t.json();return console.log("modelHubCall:",o),o}catch(e){throw console.error("Failed to create key:",e),e}},N=async(e,t,o,a,n,c,s,i)=>{try{let t="/model/metrics";a&&(t="".concat(t,"?_selected_model_group=").concat(a,"&startTime=").concat(n,"&endTime=").concat(c,"&api_key=").concat(s,"&customer=").concat(i));let o=await fetch(t,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await o.json()}catch(e){throw console.error("Failed to create key:",e),e}},P=async(e,t,o,a)=>{try{let n="/model/streaming_metrics";t&&(n="".concat(n,"?_selected_model_group=").concat(t,"&startTime=").concat(o,"&endTime=").concat(a));let c=await fetch(n,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!c.ok){let e=await c.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await c.json()}catch(e){throw console.error("Failed to create key:",e),e}},A=async(e,t,o,a,n,c,s,i)=>{try{let t="/model/metrics/slow_responses";a&&(t="".concat(t,"?_selected_model_group=").concat(a,"&startTime=").concat(n,"&endTime=").concat(c,"&api_key=").concat(s,"&customer=").concat(i));let o=await fetch(t,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await o.json()}catch(e){throw console.error("Failed to create key:",e),e}},C=async(e,t,o,a,n,c,s,i)=>{try{let t="/model/metrics/exceptions";a&&(t="".concat(t,"?_selected_model_group=").concat(a,"&startTime=").concat(n,"&endTime=").concat(c,"&api_key=").concat(s,"&customer=").concat(i));let o=await fetch(t,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await o.json()}catch(e){throw console.error("Failed to create key:",e),e}},b=async(e,t,o)=>{try{let t=await fetch("/models",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to create key:",e),e}},x=async e=>{try{let t="/global/spend/teams";console.log("in teamSpendLogsCall:",t);let o=await fetch("".concat(t),{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let a=await o.json();return console.log(a),a}catch(e){throw console.error("Failed to create key:",e),e}},B=async(e,t,o,r)=>{try{let a="/global/spend/tags";t&&o&&(a="".concat(a,"?start_date=").concat(t,"&end_date=").concat(o)),r&&(a+="".concat(a,"&tags=").concat(r.join(","))),console.log("in tagsSpendLogsCall:",a);let n=await fetch("".concat(a),{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!n.ok)throw await n.text(),Error("Network response was not ok");let c=await n.json();return console.log(c),c}catch(e){throw console.error("Failed to create key:",e),e}},z=async e=>{try{let t="/global/spend/all_tag_names";console.log("in global/spend/all_tag_names call",t);let o=await fetch("".concat(t),{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok)throw await o.text(),Error("Network response was not ok");let r=await o.json();return console.log(r),r}catch(e){throw console.error("Failed to create key:",e),e}},O=async e=>{try{let t="/global/all_end_users";console.log("in global/all_end_users call",t);let o=await fetch("".concat(t),{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok)throw await o.text(),Error("Network response was not ok");let r=await o.json();return console.log(r),r}catch(e){throw console.error("Failed to create key:",e),e}},Z=async(e,t,o,a,n,c)=>{try{console.log("user role in spend logs call: ".concat(o));let t="/spend/logs";t="App Owner"==o?"".concat(t,"?user_id=").concat(a,"&start_date=").concat(n,"&end_date=").concat(c):"".concat(t,"?start_date=").concat(n,"&end_date=").concat(c);let s=await fetch(t,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!s.ok){let e=await s.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let i=await s.json();return console.log(i),i}catch(e){throw console.error("Failed to create key:",e),e}},S=async e=>{try{let t=await fetch("/global/spend/logs",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let o=await t.json();return console.log(o),o}catch(e){throw console.error("Failed to create key:",e),e}},v=async e=>{try{let t=await fetch("/global/spend/keys?limit=5",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let o=await t.json();return console.log(o),o}catch(e){throw console.error("Failed to create key:",e),e}},G=async(e,t,o,a)=>{try{let n="";n=t?JSON.stringify({api_key:t,startTime:o,endTime:a}):JSON.stringify({startTime:o,endTime:a});let c={method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}};c.body=n;let s=await fetch("/global/spend/end_users",c);if(!s.ok){let e=await s.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let i=await s.json();return console.log(i),i}catch(e){throw console.error("Failed to create key:",e),e}},J=async(e,t,o,a)=>{try{let n="/global/spend/provider";o&&a&&(n+="?start_date=".concat(o,"&end_date=").concat(a)),t&&(n+="&api_key=".concat(t));let c=await fetch(n,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!c.ok){let e=await c.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let s=await c.json();return console.log(s),s}catch(e){throw console.error("Failed to fetch spend data:",e),e}},R=async(e,t,o)=>{try{let r="/global/activity";t&&o&&(r+="?start_date=".concat(t,"&end_date=").concat(o));let a=await fetch(r,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!a.ok)throw await a.text(),Error("Network response was not ok");let n=await a.json();return console.log(n),n}catch(e){throw console.error("Failed to fetch spend data:",e),e}},I=async(e,t,o)=>{try{let r="/global/activity/cache_hits";t&&o&&(r+="?start_date=".concat(t,"&end_date=").concat(o));let a=await fetch(r,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!a.ok)throw await a.text(),Error("Network response was not ok");let n=await a.json();return console.log(n),n}catch(e){throw console.error("Failed to fetch spend data:",e),e}},V=async(e,t,o)=>{try{let r="/global/activity/model";t&&o&&(r+="?start_date=".concat(t,"&end_date=").concat(o));let a=await fetch(r,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!a.ok)throw await a.text(),Error("Network response was not ok");let n=await a.json();return console.log(n),n}catch(e){throw console.error("Failed to fetch spend data:",e),e}},U=async(e,t,o,r)=>{try{let a="/global/activity/exceptions";t&&o&&(a+="?start_date=".concat(t,"&end_date=").concat(o)),r&&(a+="&model_group=".concat(r));let n=await fetch(a,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!n.ok)throw await n.text(),Error("Network response was not ok");let c=await n.json();return console.log(c),c}catch(e){throw console.error("Failed to fetch spend data:",e),e}},M=async(e,t,o,r)=>{try{let a="/global/activity/exceptions/deployment";t&&o&&(a+="?start_date=".concat(t,"&end_date=").concat(o)),r&&(a+="&model_group=".concat(r));let n=await fetch(a,{method:"GET",headers:{Authorization:"Bearer ".concat(e)}});if(!n.ok)throw await n.text(),Error("Network response was not ok");let c=await n.json();return console.log(c),c}catch(e){throw console.error("Failed to fetch spend data:",e),e}},X=async e=>{try{let t=await fetch("/global/spend/models?limit=5",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let o=await t.json();return console.log(o),o}catch(e){throw console.error("Failed to create key:",e),e}},q=async(e,t)=>{try{let o=await fetch("/v2/key/info",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({keys:t})});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let a=await o.json();return console.log(a),a}catch(e){throw console.error("Failed to create key:",e),e}},D=async(e,t)=>{try{let o="/user/get_users?role=".concat(t);console.log("in userGetAllUsersCall:",o);let a=await fetch(o,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!a.ok){let e=await a.text();throw r.ZP.error("Failed to delete key: "+e,10),Error("Network response was not ok")}let n=await a.json();return console.log(n),n}catch(e){throw console.error("Failed to get requested models:",e),e}},K=async e=>{try{let t=await fetch("/user/available_roles",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok)throw await t.text(),Error("Network response was not ok");let o=await t.json();return console.log("response from user/available_role",o),o}catch(e){throw e}},L=async(e,t)=>{try{console.log("Form Values in teamCreateCall:",t);let o=await fetch("/team/new",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("API Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},H=async(e,t)=>{try{console.log("Form Values in keyUpdateCall:",t);let o=await fetch("/key/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to update key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("Update key Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},Q=async(e,t)=>{try{console.log("Form Values in teamUpateCall:",t);let o=await fetch("/team/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to update team: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("Update Team Response:",a),a}catch(e){throw console.error("Failed to create key:",e),e}},W=async(e,t)=>{try{console.log("Form Values in modelUpateCall:",t);let o=await fetch("/model/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error("Failed to update model: "+e,10),console.error("Error update from the server:",e),Error("Network response was not ok")}let a=await o.json();return console.log("Update model Response:",a),a}catch(e){throw console.error("Failed to update model:",e),e}},Y=async(e,t,o)=>{try{console.log("Form Values in teamMemberAddCall:",o);let a=await fetch("/team/member_add",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({team_id:t,member:o})});if(!a.ok){let e=await a.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let n=await a.json();return console.log("API Response:",n),n}catch(e){throw console.error("Failed to create key:",e),e}},$=async(e,t,o)=>{try{console.log("Form Values in userUpdateUserCall:",t);let a={...t};null!==o&&(a.user_role=o),a=JSON.stringify(a);let n=await fetch("/user/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:a});if(!n.ok){let e=await n.text();throw r.ZP.error("Failed to create key: "+e,10),console.error("Error response from the server:",e),Error("Network response was not ok")}let c=await n.json();return console.log("API Response:",c),c}catch(e){throw console.error("Failed to create key:",e),e}},ee=async(e,t)=>{try{let o="/health/services?service=".concat(t);console.log("Checking Slack Budget Alerts service health");let a=await fetch(o,{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!a.ok){let e=await a.text();throw r.ZP.error("Failed ".concat(t," service health check ")+e),Error(e)}let n=await a.json();return r.ZP.success("Test request to ".concat(t," made - check logs/alerts on ").concat(t," to verify")),n}catch(e){throw console.error("Failed to perform health check:",e),e}},et=async e=>{try{let t=await fetch("/budget/list",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}},eo=async(e,t,o)=>{try{let t=await fetch("/get/config/callbacks",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}},er=async e=>{try{let t=await fetch("/config/list?config_type=general_settings",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}},ea=async(e,t)=>{try{let o=await fetch("/config/field/info?field_name=".concat(t),{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!o.ok)throw await o.text(),Error("Network response was not ok");return await o.json()}catch(e){throw console.error("Failed to set callbacks:",e),e}},en=async(e,t,o)=>{try{let a=await fetch("/config/field/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({field_name:t,field_value:o,config_type:"general_settings"})});if(!a.ok){let e=await a.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let n=await a.json();return r.ZP.success("Successfully updated value!"),n}catch(e){throw console.error("Failed to set callbacks:",e),e}},ec=async(e,t)=>{try{let o=await fetch("/config/field/delete",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({field_name:t,config_type:"general_settings"})});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}let a=await o.json();return r.ZP.success("Field reset on proxy"),a}catch(e){throw console.error("Failed to get callbacks:",e),e}},es=async(e,t)=>{try{let o=await fetch("/config/update",{method:"POST",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"},body:JSON.stringify({...t})});if(!o.ok){let e=await o.text();throw r.ZP.error(e,10),Error("Network response was not ok")}return await o.json()}catch(e){throw console.error("Failed to set callbacks:",e),e}},ei=async e=>{try{let t=await fetch("/health",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok){let e=await t.text();throw r.ZP.error(e),Error("Network response was not ok")}return await t.json()}catch(e){throw console.error("Failed to call /health:",e),e}},el=async e=>{try{let t=await fetch("/sso/get/logout_url",{method:"GET",headers:{Authorization:"Bearer ".concat(e),"Content-Type":"application/json"}});if(!t.ok)throw await t.text(),Error("Network response was not ok");return await t.json()}catch(e){throw console.error("Failed to get callbacks:",e),e}}}}]);