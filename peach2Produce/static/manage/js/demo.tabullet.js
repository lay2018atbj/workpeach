
function showPopup() {
    document.getElementById('white_content_pop').style.display='block';
    document.getElementById('fade_main_container').style.display='block'
}

function closePopup() {
    document.getElementById('white_content_pop').style.display='none';
    document.getElementById('fade_main_container').style.display='none'
}


function removeCheck(){
    $("input[name='device-check']:checked").each(function() {       // 遍历选中的checkbox
            n = $(this).parents("tr").index() + 1;                      // 获取checkbox所在行的顺序,+1 排除标签栏
            var deviceTr   = $("table#device-table").find("tr:eq("+n+")");
            var deviceId   = deviceTr.find("td:eq(1)").text()  ;
            var deviceIp   = deviceTr.find("td:eq(2)").text()  ;
            var devicePort = deviceTr.find("td:eq(3)").text()  ;
            alert("设备id:" + deviceId + ",host:" + deviceIp  + ",port:" + devicePort) ;
            //alert()
            $.post("/ma_config/removedevice",
                   {"id":deviceId,"ip":deviceIp,"port":devicePort},
                    function(){alert("设备id:" + deviceId + ",host:" + deviceIp  + ",port:" + devicePort+"删除成功") ;}
                    ,"json"
                   );
            $("table#device-table").find("tr:eq("+n+")").remove();
     });
}



function doConnect(){
    $("input[name='device-check']:checked").each(function() {       // 遍历选中的checkbox
            n = $(this).parents("tr").index() + 1;                      // 获取checkbox所在行的顺序,+1 排除标签栏
            var deviceTr   = $("table#device-table").find("tr:eq("+n+")");
            var deviceId   = deviceTr.find("td:eq(1)").text()  ;
            var deviceIp   = deviceTr.find("td:eq(2)").text()  ;
            var devicePort = deviceTr.find("td:eq(3)").text()  ;
            var desc       = deviceTr.find("td:eq(4)").text()  ;
            var robotId    = deviceTr.find("td:eq(5)").text()  ;

            //alert()
            $.post("/ma_config/connectdevice",
                   {"id":deviceId,"devIP":deviceIp,"devPort":devicePort,"robotId":robotId,"devDesc":desc},
                    function(){alert("设备id:" + deviceId + ",host:" + deviceIp  + ",port:" + devicePort+"重连成功") ;}
                    ,"json"
             );

     });
}

function editText(element){
     var old_html = element.innerHTML;//获得元素之前的内容
　   var new_obj = document.createElement('input');//创建一个input元素
　   new_obj.type = 'text';//为newobj元素添加类型
     new_obj.id  = 'tmp';//为newobj元素添加类型
     new_obj.value=old_html;
     new_obj.class='mws-textinput required'
　   element.innerHTML = '';　　 //设置元素内容为空
　   element.appendChild(new_obj);//添加子元素
　   new_obj.focus();//获得焦点
     //设置newobj失去焦点的事件
　   new_obj.onblur = function(){
            //当触发时判断newobj的值是否为空，为空则不修改，并返回old_html
            element.innerHTML = this.value ? this.value : old_html;
                         // 获取checkbox所在行的顺序,+1 排除标签栏
            //null
     }
}

function updateCheck(){
    $("input[name='device-check']:checked").each(function() {       // 遍历选中的checkbox
            n = $(this).parents("tr").index() + 1;                      // 获取checkbox所在行的顺序,+1 排除标签栏
            var deviceTr   = $("table#device-table").find("tr:eq("+n+")");
            var deviceId   = deviceTr.find("td:eq(1)").text()  ;
            var deviceIp   = deviceTr.find("td:eq(2)").text()  ;
            var devicePort = deviceTr.find("td:eq(3)").text()  ;
            var deviceDesc = deviceTr.find("td:eq(4)").text()  ;
            var robotId    = deviceTr.find("td:eq(5)").text()  ;
            //alert()
            $.post("/ma_config/adddevice",{"devDesc":deviceDesc, "devIP":deviceIp,"devPort":devicePort,"robotId":robotId},
                    function(){alert("设备id:" + deviceId + ",host:" + deviceIp  + ",port:" + devicePort+"重连成功") ;}
                    ,"json"
             );

     });
}
