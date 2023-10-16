
html = '''
         <tr>
                            <td data-title="IP">61.216.185.88</td>
                            <td data-title="PORT">60808</td>
                            <td data-title="匿名度">高匿名</td>
                            <td data-title="类型">HTTP</td>
                            <td data-title="位置">中国 台湾 屏东县 </td>
                            <td data-title="响应速度">0.7秒</td>
                            <td data-title="最后验证时间">2023-09-28 20:31:01</td>
                            <td data-title="付费方式">免费代理ip</td>
                        </tr>
                    
                        <tr>
                            <td data-title="IP">36.134.91.82</td>
                            <td data-title="PORT">8888</td>
                            <td data-title="匿名度">高匿名</td>
                            <td data-title="类型">HTTP</td>
                            <td data-title="位置">中国   </td>
                            <td data-title="响应速度">5秒</td>
                            <td data-title="最后验证时间">2023-09-28 19:31:01</td>
                            <td data-title="付费方式">免费代理ip</td>
                        </tr>

'''

html2 = '''
 <td>139.196.214.238</td>
                    <td>2087</td>
                    
                    
                     <td>139.196.214.238</td>
                    <td>2087</td>
'''

html3 = '''

 <td data-title="IP">180.123.9.124</td>
                            <td data-title="PORT">8888</td>
'''
import re

r = re.findall('<td data-title="IP">(.*?)</td>[\s\S]*?<td data-title="PORT">(.*?)</td>',html3)
print(r)


r = re.findall('<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',html2)
print(r)