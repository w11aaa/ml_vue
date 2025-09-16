import router from './index'
export default function(path,query,title){
	let nowPath = this.$route.path.replace("/","")
	if(nowPath!=path){
		router.addRoute(
			{
				path:"/"+path,
				component:() => import("@/views/"+path),
			}
		)
		router.push({path,query})
		document.title = title
	}
}