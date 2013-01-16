package test;

public class Console {
	
	public static void main(String[] argv){
		//Create socket connection
		//System.out.println("jar cf jar-file input-file(s)");
		//if(1==1)return;
		int i = 0;
		for(i = 0 ; i < 10000 ; i++){
			System.out.println(i);
			MultiClients client = new MultiClients();
			client.start();
			System.out.println(i + " ends");
			/*try {
				Thread.sleep(1);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}*/
		}
		
	}

}
